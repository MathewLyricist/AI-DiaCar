import os
os.environ["CHROMA_MEMORY_LIMIT_BYTES"] = "8589934592"
import logging
from typing import List, Dict, Optional
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from app.config import settings
from app.services.pdf_processor import PDFProcessor

logger = logging.getLogger(__name__)


class VectorStore:

    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL,
            model_kwargs={'device': 'cpu'}
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        self.vectorstore: Optional[Chroma] = None
        self.pdf_processor = PDFProcessor()
        logger.info(f"Путь к мануалам: {settings.MANUALS_PATH}")
        if not os.path.exists(settings.MANUALS_PATH):
            logger.error(f"❌ Директория мануалов не существует: {settings.MANUALS_PATH}")

    def initialize(self, force_reindex=False):
        os.makedirs(settings.VECTORSTORE_PATH, exist_ok=True)

        if not force_reindex and os.path.exists(settings.VECTORSTORE_PATH) and os.listdir(settings.VECTORSTORE_PATH):
            self.vectorstore = Chroma(
                persist_directory=settings.VECTORSTORE_PATH,
                embedding_function=self.embeddings
            )
            logger.info("✅ Загружено существующее векторное хранилище")
            return

        self.vectorstore = Chroma(
            persist_directory=settings.VECTORSTORE_PATH,
            embedding_function=self.embeddings
        )
        logger.info("🆕 Создано новое векторное хранилище")

    def index_manuals(self, force=False):

        if not self.vectorstore:
            self.initialize(force_reindex=force)

        if not force and self.vectorstore._collection.count() > 0:
            logger.info(f"ℹ️ Векторное хранилище уже содержит {self.vectorstore._collection.count()} фрагментов. Индексация пропущена.")
            return

        if force:
            logger.warning("⚠️ Принудительная переиндексация: очищаем коллекцию")
            self.vectorstore.delete_collection()
            self.vectorstore = None
            self.initialize(force_reindex=True)

        manuals_data = self.pdf_processor.scan_manuals()
        logger.info(f"📄 Найдено мануалов: {len(manuals_data)}")

        total_chunks = 0
        for manual in manuals_data:
            logger.info(f"📖 Индексация: {manual['pdf_path']}, тип {manual['manual_type']}")
            for page in manual['pages']:
                chunks = self.text_splitter.split_text(page['text'])
                for chunk in chunks:
                    metadata = {
                        "pdf_path": manual['pdf_path'],
                        "page_number": page['page_number'],
                        "manual_type": manual['manual_type'],
                        "chunk_text": chunk
                    }
                    self.vectorstore.add_texts(texts=[chunk], metadatas=[metadata])
                    total_chunks += 1
            import gc
            gc.collect()

        logger.info(f"✅ Проиндексировано {len(manuals_data)} мануалов, {total_chunks} фрагментов")

    def search(self, query: str, top_k: int = None, manual_type: str = None) -> List[Dict]:
        if not self.vectorstore:
            self.initialize()

        top_k = top_k or settings.TOP_K_RESULTS

        filter_metadata = {}
        if manual_type:
            filter_metadata["manual_type"] = manual_type

        results = self.vectorstore.similarity_search_with_score(
            query=query,
            k=top_k,
            filter=filter_metadata if filter_metadata else None
        )

        filtered_results = []
        for doc, score in results:
            if score >= settings.SCORE_THRESHOLD:
                filtered_results.append({
                    "text": doc.page_content,
                    "metadata": doc.metadata,
                    "score": float(score)
                })

        return filtered_results

    def search_with_context(self, query: str, car_info: Dict) -> List[Dict]:
        results = []
        top_k = settings.TOP_K_RESULTS

        if car_info.get('brand') and car_info.get('model'):
            specific_results = self.search(
                query=query,
                top_k=top_k,
                manual_type="SPECIFIC"
            )
            results.extend(specific_results)

        if len(results) < top_k:
            brand_results = self.search(
                query=query,
                top_k=top_k - len(results),
                manual_type="BRAND_COMMON"
            )
            results.extend(brand_results)

        if len(results) < top_k:
            general_results = self.search(
                query=query,
                top_k=top_k - len(results),
                manual_type="GENERAL"
            )
            results.extend(general_results)

        return results[:top_k]