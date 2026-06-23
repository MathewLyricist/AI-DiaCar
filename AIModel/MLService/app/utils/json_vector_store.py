import logging
import os
from pathlib import Path
from typing import List, Dict, Optional, Any

from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from app.config import settings
from app.utils.knowledge_loader import knowledge_loader

logger = logging.getLogger(__name__)

class JsonVectorStore:

    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL,
            model_kwargs={'device': 'cpu'}
        )
        self.persist_dir = settings.JSON_VECTORSTORE_PATH
        os.makedirs(self.persist_dir, exist_ok=True)
        self.vectorstore: Optional[Chroma] = None
        self._loaded_models = set()

        if os.path.exists(self.persist_dir) and os.listdir(self.persist_dir):
            try:
                self.vectorstore = Chroma(
                    persist_directory=self.persist_dir,
                    embedding_function=self.embeddings,
                    collection_name="json_issues"
                )
                if self.vectorstore._collection.count() > 0:
                    logger.info("Загружено существующее векторное хранилище JSON")
                else:
                    self.vectorstore = None
            except Exception as e:
                logger.warning(f"Не удалось загрузить существующее хранилище: {e}")
                self.vectorstore = None

    def _ensure_initialized(self):
        if self.vectorstore is None:
            self.vectorstore = Chroma(
                persist_directory=self.persist_dir,
                embedding_function=self.embeddings,
                collection_name="json_issues"
            )

    def _index_model(self, brand: str, model: str):
        key = (brand.lower(), model.lower())
        if key in self._loaded_models:
            return

        logger.info(f"Индексация записей для {brand}/{model} в векторное хранилище")
        entries = knowledge_loader.get_entries(brand, model)
        if not entries:
            logger.warning(f"Нет записей для {brand}/{model}")
            return

        self._ensure_initialized()
        texts = []
        metadatas = []
        for entry in entries:
            parts = []
            parts.append(entry.get("title", ""))
            if entry.get("tags"):
                parts.append(" ".join(entry["tags"]))
            if entry.get("symptoms"):
                parts.append(" ".join(entry["symptoms"]))
            if entry.get("diagnosis"):
                parts.append(entry["diagnosis"])
            text = " ".join(parts).strip()
            if not text:
                text = entry.get("title", "unknown")
            texts.append(text)

            metadata = {
                "brand": entry.get("brand", brand).lower(),
                "model": entry.get("model", model).lower(),
                "title": entry.get("title", ""),
                "tags": ",".join(entry.get("tags", [])),
                "confidence": entry.get("confidence", 0.5),
                "manual_reference": entry.get("manual_reference", ""),
                "source": entry.get("source", ""),
                "year_from": entry.get("year_from"),
                "year_to": entry.get("year_to"),
                "diagnosis": entry.get("diagnosis", ""),
                "solution": entry.get("solution", ""),
                "additional_info": entry.get("additional_info", ""),
            }
            metadatas.append(metadata)

        try:
            filter_old = {"$and": [{"brand": brand.lower()}, {"model": model.lower()}]}
            existing = self.vectorstore.get(where=filter_old)
            if existing and existing['ids']:
                self.vectorstore.delete(ids=existing['ids'])
                logger.info(f"Удалены старые записи для {brand}/{model} ({len(existing['ids'])} док.)")
        except Exception as e:
            logger.warning(f"Не удалось удалить старые записи: {e}")

        self.vectorstore.add_texts(texts=texts, metadatas=metadatas)
        self._loaded_models.add(key)
        logger.info(f"Индексировано {len(entries)} записей для {brand}/{model}")

    def search(self, brand: str, model: str, query: str, year: int = None, top_k: int = None) -> List[Dict]:

        if not brand or not model:
            return []
        self._ensure_initialized()
        self._index_model(brand, model)

        top_k = top_k or settings.JSON_SEARCH_TOP_K
        threshold = settings.JSON_SIMILARITY_THRESHOLD

        filter_dict = {"$and": [{"brand": brand.lower()}, {"model": model.lower()}]}
        try:
            results = self.vectorstore.similarity_search_with_score(
                query=query, k=top_k, filter=filter_dict
            )
        except Exception as e:
            logger.error(f"Ошибка поиска: {e}")
            return []

        output = []
        for doc, score in results:
            if score < threshold:
                continue
            meta = doc.metadata
            if year is not None:
                yf = meta.get("year_from")
                yt = meta.get("year_to")
                if yf is not None and yt is not None and not (yf <= year <= yt):
                    continue

            entry = {
                "title": meta.get("title", ""),
                "tags": meta.get("tags", "").split(",") if meta.get("tags") else [],
                "confidence": meta.get("confidence", 0.5),
                "manual_reference": meta.get("manual_reference", ""),
                "source": meta.get("source", ""),
                "diagnosis": meta.get("diagnosis", ""),
                "solution": meta.get("solution", ""),
                "additional_info": meta.get("additional_info", ""),
                "year_from": meta.get("year_from"),
                "year_to": meta.get("year_to"),
                "brand": meta.get("brand", brand),
                "model": meta.get("model", model),
            }
            for k in ["symptoms", "removal_steps", "required_tools", "consumables", "preparation", "set_tdc"]:
                if k in doc.metadata:
                    entry[k] = doc.metadata[k]

            output.append({
                "entry": entry,
                "score": float(score),
                "manual_reference": meta.get("manual_reference", "")
            })
        return output

json_vector_store = JsonVectorStore()