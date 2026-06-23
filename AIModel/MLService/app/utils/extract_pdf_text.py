import os, json, logging
from pdfplumber import open as pdf_open
from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_all_text():
    all_docs = []
    for root, _, files in os.walk(settings.MANUALS_PATH):
        for file in files:
            if not file.lower().endswith('.pdf'): continue
            pdf_path = os.path.join(root, file)
            try:
                pages_text = []
                with pdf_open(pdf_path) as pdf:
                    for page in pdf.pages:
                        text = page.extract_text() or ""
                        pages_text.append(text)
                all_docs.append({
                    "path": pdf_path,
                    "pages": pages_text,
                    "full_text": "\n".join(pages_text),
                })
                logger.info(f"Извлечено: {pdf_path} ({len(pages_text)} стр.)")
            except Exception as e:
                logger.error(f"Ошибка {pdf_path}: {e}")
    with open("./data/pdf_texts.json", "w", encoding="utf-8") as f:
        json.dump(all_docs, f, ensure_ascii=False, indent=2)
    logger.info(f"Сохранено {len(all_docs)} документов")

if __name__ == "__main__":
    extract_all_text()