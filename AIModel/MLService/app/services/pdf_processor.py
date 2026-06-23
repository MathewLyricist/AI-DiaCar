import os
import re
import logging
from typing import List, Dict, Optional
import pdfplumber
from pdf2image import convert_from_path
import pytesseract
from app.config import settings

logger = logging.getLogger(__name__)


class PDFProcessor:

    def __init__(self):
        self.manuals_path = settings.MANUALS_PATH

    def extract_text_by_pages(self, pdf_path: str) -> List[Dict]:
        pages_data = []
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for i, page in enumerate(pdf.pages, 1):
                    page_text = page.extract_text()
                    if not page_text or len(page_text.strip()) < 30:
                        logger.debug(f"Страница {i} - мало текста ({len(page_text or '')} симв.), использую OCR")
                        page_text = self._extract_page_ocr(pdf_path, i)
                    else:
                        page_text = self._basic_clean(page_text)

                    if page_text and len(page_text.strip()) > 20:
                        pages_data.append({
                            "page_number": i,
                            "text": page_text,
                            "pdf_path": pdf_path
                        })

                    if i % 10 == 0:
                        import gc
                        gc.collect()

            return pages_data
        except Exception as e:
            logger.error(f"Ошибка извлечения текста по страницам из {pdf_path}: {e}")
            return []

    def _extract_page_ocr(self, pdf_path: str, page_number: int) -> str:
        try:
            images = convert_from_path(
                pdf_path,
                first_page=page_number,
                last_page=page_number,
                dpi=150
            )
            if images:
                text = pytesseract.image_to_string(images[0], lang='rus+eng')
                text = self._basic_clean(text)
                return text
            return ""
        except Exception as e:
            logger.error(f"Ошибка OCR страницы {page_number}: {e}")
            return ""

    def _basic_clean(self, text: str) -> str:
        if not text:
            return text
        for artifact in ['in fo', 'www.', 'Рис.', 'см. с.']:
            text = text.replace(artifact, '')
        text = ' '.join(text.split())
        return text.strip()

    def scan_manuals(self) -> List[Dict]:
        manuals_data = []

        if not os.path.exists(self.manuals_path):
            logger.error(f"❌ Директория мануалов не найдена: {self.manuals_path}")
            return manuals_data

        logger.info(f"📂 Сканирование мануалов в: {self.manuals_path}")

        for root, dirs, files in os.walk(self.manuals_path):
            for file in files:
                if file.lower().endswith('.pdf'):
                    pdf_path = os.path.join(root, file)
                    logger.info(f"📄 Найден PDF: {pdf_path}")

                    manual_type = self._determine_manual_type(pdf_path)
                    pages = self.extract_text_by_pages(pdf_path)

                    if pages:
                        total_text = sum(len(p['text']) for p in pages)
                        manuals_data.append({
                            "pdf_path": pdf_path,
                            "manual_type": manual_type,
                            "pages": pages,
                            "total_pages": len(pages),
                            "total_text_length": total_text
                        })
                        logger.info(f"✅ Обработано: {pdf_path} ({len(pages)} страниц, {total_text} символов)")
                    else:
                        logger.warning(f"⚠️ Не удалось извлечь текст: {pdf_path}")

        logger.info(f"📊 Всего обработано мануалов: {len(manuals_data)}")
        return manuals_data

    def _determine_manual_type(self, pdf_path: str) -> str:
        if "/Common/" in pdf_path or "\\Common\\" in pdf_path:
            if pdf_path.count(os.sep) <= 3:
                return "GENERAL"
            else:
                return "BRAND_COMMON"
        else:
            return "SPECIFIC"