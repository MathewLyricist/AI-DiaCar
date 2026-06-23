import logging
import gc
import ctypes
from pathlib import Path
from pdfplumber import open as pdf_open

logger = logging.getLogger(__name__)


def trim_memory() -> int:
    try:
        libc = ctypes.CDLL("libc.so.6")
        return libc.malloc_trim(0)
    except (OSError, AttributeError):
        return 0


def cache_pdf_text(pdf_path: str) -> bool:
    pdf_file = Path(pdf_path)
    if not pdf_file.exists():
        return False

    txt_path = pdf_file.with_suffix('.txt')
    if txt_path.exists():
        return True

    try:
        with pdf_open(pdf_file) as pdf:
            total_pages = len(pdf.pages)
            with open(txt_path, 'w', encoding='utf-8') as out_f:
                for page_num in range(total_pages):
                    page = pdf.pages[page_num]
                    page_text = page.extract_text()
                    if page_text:
                        out_f.write(f"\n=== СТРАНИЦА {page_num + 1} ===\n")
                        out_f.write(page_text)
                        out_f.write("\n")

                    page.flush_cache()

                    if hasattr(page, '_objects'):
                        del page._objects
                    if hasattr(page, '_layout'):
                        del page._layout

                    gc.collect()

                    trim_memory()

            return True

    except Exception as e:
        logger.error(f"Ошибка кэширования {pdf_path}: {e}")
        return False


def get_cached_text(pdf_path: str) -> str:
    pdf_file = Path(pdf_path)
    if not pdf_file.exists():
        logger.warning(f"PDF не найден: {pdf_path}")
        return ""

    txt_path = pdf_file.with_suffix('.txt')
    if txt_path.exists():
        try:
            with open(txt_path, 'r', encoding='utf-8') as f:
                text = f.read()
                logger.info(f"Загружен кэш из {txt_path} ({len(text)} символов)")
                return text
        except Exception as e:
            logger.error(f"Ошибка чтения кэша {txt_path}: {e}")

    if cache_pdf_text(pdf_path):
        try:
            with open(txt_path, 'r', encoding='utf-8') as f:
                return f.read()
        except:
            return ""
    return ""