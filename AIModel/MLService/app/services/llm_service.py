import logging
import requests
from typing import List, Dict, Optional

from app.config import settings

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.enabled = settings.LLM_ENABLED and bool(settings.OPENROUTER_API_KEY)
        self.api_key = settings.OPENROUTER_API_KEY
        self.model = settings.OPENROUTER_MODEL
        self.url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "AI DiaCar ML Service"
        }
        if self.enabled:
            logger.info(f"LLM через OpenRouter включён (модель: {self.model})")
        else:
            logger.warning("LLM через OpenRouter отключён (нет API-ключа или LLM_ENABLED=False)")

    def generate_answer(self, user_query: str, entries: List[Dict]) -> Optional[str]:
        if not self.enabled or not self.api_key:
            logger.warning("OpenRouter недоступен")
            return None

        if not entries:
            return None

        prompt = self._build_prompt(user_query, entries)
        try:
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": settings.LLM_TEMPERATURE,
                "max_tokens": settings.LLM_MAX_NEW_TOKENS
            }
            response = requests.post(self.url, headers=self.headers, json=payload, timeout=30)
            if response.status_code == 200:
                data = response.json()
                answer = data["choices"][0]["message"]["content"].strip()
                logger.info(f"OpenRouter сгенерировал ответ длиной {len(answer)} символов")
                return answer
            else:
                logger.error(f"OpenRouter ошибка {response.status_code}: {response.text}")
                return None
        except Exception as e:
            logger.error(f"Ошибка вызова OpenRouter: {e}")
            return None

    def _build_prompt(self, query: str, entries: List[Dict]) -> str:
        context_parts = []
        for i, entry in enumerate(entries, 1):
            title = entry.get("title", "Неизвестная проблема")
            diagnosis = entry.get("diagnosis", "")
            solution = entry.get("solution", "")
            additional = entry.get("additional_info", "")
            part = f"Запись {i}: {title}.\n"
            if diagnosis:
                part += f"Диагноз: {diagnosis}\n"
            if solution:
                part += f"Решение: {solution}\n"
            if additional:
                part += f"Дополнительно: {additional}\n"
            context_parts.append(part)
        context = "\n".join(context_parts)

        prompt = f"""Вопрос пользователя: {query}

Используй следующую информацию из технической документации:
{context}

Дай понятный, естественный ответ на русском языке. Не перечисляй диагноз и решение как отдельные пункты, а объедини их в связный текст. Если есть несколько вариантов, предложи их. Не добавляй информацию, которой нет выше.
Ответ:"""
        return prompt

llm_service = None