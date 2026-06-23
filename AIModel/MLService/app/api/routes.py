import logging
import re
import os
from typing import List, Dict, Optional
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.api.schemas import QueryRequest, QueryResponse
from app.database import get_db
from app.services.query_analyzer import QueryAnalyzer
from app.utils.text_cleaner import clean_text
from app.utils.clarification_loader import clarification_loader
from app.utils.knowledge_loader import knowledge_loader
from app.services.pdf_parser_service import PDFParserService
from app.utils.pdf_cache import get_cached_text
from app.utils.json_vector_store import json_vector_store
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

analyzer = QueryAnalyzer()
pdf_parser = PDFParserService()

HIGH_THRESHOLD = getattr(settings, "HIGH_THRESHOLD", 7.5)
LOW_THRESHOLD = getattr(settings, "LOW_THRESHOLD", 6.0)

def extract_pages_from_reference(ref: str) -> List[int]:
    if not ref:
        return []
    match_range = re.search(r'(\d+)\s*[-–]\s*(\d+)', ref)
    if match_range:
        start = int(match_range.group(1))
        end = int(match_range.group(2))
        return list(range(start, end + 1))
    numbers = re.findall(r'\b(\d+)\b', ref)
    return [int(n) for n in numbers if int(n) < 1000 and int(n) > 0]

@router.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest, req: Request, db: Session = Depends(get_db), vs=None):
    logger.info(f"🔍 Запрос: '{request.message}', сессия {request.session_id}")
    logger.info(f"📄 PDF path from request: {request.pdf_path}")

    analysis = analyzer.analyze(request.message)
    keywords = analysis["keywords"]
    logger.info(f"Ключевые слова: {keywords}")

    car_info = request.car_info
    brand = car_info.brand if car_info else None
    model = car_info.model if car_info else None

    entries = []
    best_entry = None
    max_score = 0.0

    if brand and model:
        year = car_info.year if car_info else None
        try:
            top_k_for_llm = settings.JSON_SEARCH_TOP_K
            results = json_vector_store.search(brand, model, request.message, year=year, top_k=top_k_for_llm)
            if results:
                entries = [r["entry"] for r in results]
                best_entry = entries[0]
                max_score = max([r["score"] for r in results])
                logger.info(f"✅ Векторный поиск нашёл {len(entries)} записей, лучшая оценка {max_score:.2f}")
            else:
                logger.info("Векторный поиск не вернул результатов")
        except Exception as e:
            logger.error(f"Ошибка векторного поиска: {e}")

        if not best_entry:
            best_entry = knowledge_loader.find(brand, model, keywords, year=year)
            if best_entry:
                entries = [best_entry]
                max_score = best_entry.get("confidence", 0.5)
                logger.info(f"✅ Fallback: эвристический поиск нашёл запись (score ~ {max_score})")
            else:
                logger.warning(f"❌ Не найдено в JSON для {brand}/{model}")

    if best_entry:
        if max_score >= LOW_THRESHOLD:
            llm_service = req.app.state.llm_service
            generated_answer = None
            if llm_service and llm_service.enabled:
                generated_answer = llm_service.generate_answer(request.message, entries)
                if generated_answer and len(generated_answer) < 100:
                    logger.warning("LLM вернул слишком короткий ответ, игнорируем")
                    generated_answer = None
                if generated_answer and any(phrase in generated_answer.lower() for phrase in ["неизвестно", "противотуманной фаре", "лампы прот"]):
                    logger.warning("LLM вернул неприемлемый ответ, используем шаблон")
                    generated_answer = None
            if generated_answer:
                answer = generated_answer
                logger.info(f"✅ Ответ сгенерирован LLM (оценка {max_score:.2f})")
            else:
                answer = format_answer_from_entry(best_entry, request.message)
                logger.info(f"⚠️ Использован шаблонный ответ (оценка {max_score:.2f})")

            ref = best_entry.get("manual_reference") or best_entry.get("source")
            suggested_pages = []
            if ref and request.pdf_path and os.path.exists(request.pdf_path):
                page_numbers = extract_pages_from_reference(ref)
                suggested_pages = [{"page": p, "pdf_path": request.pdf_path} for p in page_numbers]

            clarifications = clarification_loader.get_questions(keywords)
            return QueryResponse(
                answer=answer,
                sources=[],
                suggested_pages=suggested_pages,
                clarification_questions=clarifications,
                session_id=request.session_id
            )
        else:
            logger.info(f"❌ Низкая оценка {max_score:.2f} < {LOW_THRESHOLD}, переходим к PDF")
    else:
        logger.info("Нет записей в JSON, переходим к PDF")

    pdf_text = ""
    if request.pdf_path:
        pdf_text = get_cached_text(request.pdf_path)
    elif request.context:
        pdf_text = request.context

    if pdf_text and len(pdf_text) > 500:
        cleaned_context = clean_text(pdf_text)
        blocks = pdf_parser.find_relevant_blocks(cleaned_context, keywords)
        good_blocks = []
        for block in blocks:
            block_lower = block.lower()
            if len(block) > 150 and any(kw in block_lower for kw in keywords):
                if any(kw in block_lower for kw in ['снимите', 'установите', 'замените', 'отверните', 'выверните', 'проверьте', 'отрегулируйте']):
                    good_blocks.append(block)
        if good_blocks:
            answer = format_answer_from_blocks(good_blocks, request.message)
            logger.info(f"✅ Найдено {len(good_blocks)} релевантных блоков в PDF")
            clarifications = clarification_loader.get_questions(keywords)
            return QueryResponse(
                answer=answer,
                sources=[],
                suggested_pages=[],
                clarification_questions=clarifications,
                session_id=request.session_id
            )
        else:
            answer = "❌ Информация не найдена в технической документации."
    else:
        answer = "❌ Недостаточно текста из документации (PDF не передан или слишком короткий)."

    clarifications = clarification_loader.get_questions(keywords)
    return QueryResponse(
        answer=answer,
        sources=[],
        suggested_pages=[],
        clarification_questions=clarifications,
        session_id=request.session_id
    )

def format_answer_from_vector_results(results: list, query: str) -> str:
    if not results:
        return f"❌ Не найдено по запросу \"{query}\"."
    answer = f"🔧 **{query}**\n\n"
    for i, res in enumerate(results, 1):
        text = res['text'][:500]
        answer += f"**Фрагмент {i}:**\n{text}\n\n"
    answer += "💡 Информация из технической документации."
    return answer

def format_answer_from_entry(entry: dict, query: str) -> str:
    answer = f"🔧 **{entry.get('title', query)}**\n\n"
    if entry.get("diagnosis"):
        answer += f"**Диагноз:** {entry['diagnosis']}\n\n"
    if entry.get("solution"):
        answer += f"**Решение:** {entry['solution']}\n\n"
    if entry.get("removal_steps"):
        answer += "**Порядок замены:**\n"
        steps_dict = entry["removal_steps"]
        if isinstance(steps_dict, dict):
            if "SOHC" in steps_dict and steps_dict["SOHC"]:
                answer += "\n*Для двигателей SOHC (8V):*\n"
                for i, step in enumerate(steps_dict["SOHC"], 1):
                    answer += f"{i}. {step}\n"
            if "DOHC" in steps_dict and steps_dict["DOHC"]:
                answer += "\n*Для двигателей DOHC (16V):*\n"
                for i, step in enumerate(steps_dict["DOHC"], 1):
                    answer += f"{i}. {step}\n"
        elif isinstance(steps_dict, list):
            for i, step in enumerate(steps_dict, 1):
                answer += f"{i}. {step}\n"
        answer += "\n"
    if entry.get("required_tools"):
        tools = entry["required_tools"]
        if isinstance(tools, list):
            answer += "**Необходимые инструменты:**\n"
            for tool in tools[:8]:
                answer += f"- {tool}\n"
            if len(tools) > 8:
                answer += f"- ... и ещё {len(tools) - 8}\n"
        answer += "\n"
    if entry.get("consumables"):
        cons = entry["consumables"]
        if isinstance(cons, list):
            answer += "**Расходные материалы:**\n"
            for c in cons[:6]:
                answer += f"- {c}\n"
            if len(cons) > 6:
                answer += f"- ... и ещё {len(cons) - 6}\n"
        answer += "\n"
    if entry.get("preparation"):
        prep = entry["preparation"]
        if isinstance(prep, list):
            answer += "**Подготовка:**\n"
            for p in prep[:4]:
                answer += f"- {p}\n"
            answer += "\n"
    if entry.get("set_tdc"):
        tdc = entry["set_tdc"]
        if isinstance(tdc, dict):
            common = tdc.get("common")
            if common:
                answer += f"**Установка ВМТ:** {common}\n"
        answer += "\n"
    if entry.get("additional_info"):
        answer += f"**Дополнительно:** {entry['additional_info']}\n\n"
    if entry.get("manual_reference"):
        answer += f"**Источник:** {entry['manual_reference']}\n"
    answer += "💡 Информация из базы знаний."
    return answer

def format_answer_from_blocks(blocks: list, query: str) -> str:
    if not blocks:
        return f"❌ Не найдено по запросу \"{query}\"."
    answer = f"🔧 **{query}**\n\n"
    for i, block in enumerate(blocks, 1):
        answer += f"**Инструкция {i}:**\n{block}\n\n"
    answer += "💡 Информация из технической документации."
    return answer