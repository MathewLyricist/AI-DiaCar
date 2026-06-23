import sys
import multiprocessing as mp
from pathlib import Path

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False
    print("Установите tqdm: pip install tqdm", file=sys.stderr)

sys.path.insert(0, str(Path(__file__).parent.parent))
from app.utils.pdf_cache import cache_pdf_text
from app.config import settings

def process_one(pdf_path_str: str) -> tuple[str, bool]:
    result = cache_pdf_text(pdf_path_str)
    return Path(pdf_path_str).name, result

def main():
    root = Path(settings.MANUALS_PATH)
    if not root.exists():
        print(f"Директория {root} не найдена")
        return

    pdf_files = sorted(root.rglob("*.pdf"))
    total = len(pdf_files)
    print(f"Найдено PDF: {total}")

    success_count = 0
    error_count = 0

    with mp.Pool(processes=1, maxtasksperchild=1) as pool:
        if TQDM_AVAILABLE:
            pbar = tqdm(total=total, desc="Кэширование PDF", unit="файл",
                        bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]")
        else:
            pbar = None

        for idx, pdf in enumerate(pdf_files, 1):
            filename = pdf.name
            if pbar:
                tqdm.write(f"[{idx}/{total}] Обработка: {filename}")
                pbar.set_postfix_str(filename[:40])
            else:
                print(f"[{idx}/{total}] Обработка: {filename}")

            future = pool.apply_async(process_one, (str(pdf),))
            try:
                result_filename, success = future.get(timeout=3600)
                if success:
                    success_count += 1
                else:
                    error_count += 1
                    if not pbar:
                        print(f"  ОШИБКА: {result_filename}")
            except Exception as e:
                error_count += 1
                if not pbar:
                    print(f"  ИСКЛЮЧЕНИЕ: {pdf.name}: {e}")

            if pbar:
                pbar.update(1)

        if pbar:
            pbar.close()

    print(f"\nГотово. Успешно: {success_count}, Ошибок: {error_count}")

if __name__ == "__main__":
    mp.set_start_method('spawn', force=True)
    main()