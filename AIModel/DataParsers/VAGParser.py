
"""📥 VWTS.RU PDF Downloader
Скачивает PDF-файлы по списку ссылок

Использование:
    python vwts_downloader.py links.txt [-o папка] [-d задержка]
"""

import os, re, time, argparse
from pathlib import Path
from urllib.parse import urlparse, unquote
import requests

# ==================== НАСТРОЙКИ ====================
DEFAULT_OUTPUT_DIR = "vwts_downloads"
DEFAULT_REQUEST_DELAY = 3
MAX_RETRIES = 3
REQUEST_TIMEOUT = 120
MIN_FILE_SIZE = 1024

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/pdf,*/*;q=0.8',
    'Accept-Language': 'ru-RU,ru;q=0.9',
    'Referer': 'https://vwts.ru/',
    'Connection': 'keep-alive',
    'DNT': '1',
}


# ==================== КЛАСС ЗАГРУЗЧИКА ====================
class VWTSDownloader:
    def __init__(self, output_dir: str, request_delay: float, verbose: bool = False):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.request_delay = request_delay
        self.verbose = verbose
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.stats = {'ok': 0, 'fail': 0, 'skipped': 0, 'total_bytes': 0}

    def _log(self, message: str, level: str = 'info'):
        if level == 'debug' and not self.verbose:
            return
        prefix = {'info': '', 'success': '✅ ', 'warning': '⚠️ ', 'error': '❌ ', 'debug': '🔍 '}.get(level, '')
        print(f"{prefix}{message}")

    def _sanitize_filename(self, name: str) -> str:
        name = unquote(name)
        name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', name)
        name = re.sub(r'_+', '_', name)
        return name.strip('_')[:200]

    def _is_pdf_content(self, content: bytes) -> bool:
        return content.startswith(b'%PDF-')

    def load_links(self, links_file: str) -> list:
        links = []
        try:
            with open(links_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith('#') or line.startswith('//'):
                        continue
                    if ',' in line and line.startswith('"http'):
                        line = line.split('","')[0].strip('"')
                    if line.startswith('http') and '.pdf' in line.lower():
                        if line not in links:
                            links.append(line)

            self._log(f"Загружено уникальных ссылок: {len(links)}")
            return links

        except FileNotFoundError:
            print(f"❌ Файл не найден: {links_file}")
            return []
        except Exception as e:
            print(f"❌ Ошибка чтения файла: {e}")
            return []

    def download_file(self, url: str, filename: str, skip_existing: bool = False) -> bool:
        filepath = self.output_dir / filename

        if filepath.exists():
            file_size = filepath.stat().st_size
            if file_size > MIN_FILE_SIZE and self._is_pdf_content(filepath.read_bytes()[:8]):
                if skip_existing:
                    self._log(f"Пропущено: {filename}", 'debug')
                    self.stats['skipped'] += 1
                    return True

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                resp = self.session.get(url, timeout=REQUEST_TIMEOUT)
                resp.raise_for_status()
                content = resp.content

                if self._is_pdf_content(content[:8]):
                    with open(filepath, 'wb') as f:
                        f.write(content)

                    file_size = filepath.stat().st_size
                    size_mb = file_size / (1024 * 1024)
                    self.stats['total_bytes'] += file_size

                    self._log(f"{filename} ({size_mb:.2f} MB)", 'success')
                    self.stats['ok'] += 1
                    return True

                content_type = resp.headers.get('Content-Type', '').lower()
                if 'text/html' in content_type:
                    if attempt < MAX_RETRIES:
                        wait_time = 2 + attempt
                        self._log(f"Таймер... ждём {wait_time}с ({attempt}/{MAX_RETRIES})", 'debug')
                        time.sleep(wait_time)
                        continue
                    else:
                        self._log(f"Получен HTML вместо PDF", 'warning')

            except requests.exceptions.Timeout:
                if attempt < MAX_RETRIES:
                    time.sleep(2)
            except requests.exceptions.ConnectionError:
                if attempt < MAX_RETRIES:
                    time.sleep(3)
            except requests.exceptions.HTTPError as e:
                status_code = e.response.status_code if e.response else 'N/A'
                if status_code == 429:
                    self._log(f"Блокировка! Увеличьте задержку (-d)", 'warning')
                    break
                if attempt < MAX_RETRIES:
                    time.sleep(2)
            except Exception as e:
                if attempt < MAX_RETRIES:
                    time.sleep(2)

        self._log(f"Не удалось: {filename}", 'error')
        self.stats['fail'] += 1
        return False

    def run(self, links_file: str, skip_existing: bool = False):
        print(f"📁 Выходная папка: {self.output_dir.absolute()}")
        print(f"⏱️ Задержка: {self.request_delay}с | Повторы: {MAX_RETRIES}")
        print("-" * 70)

        links = self.load_links(links_file)
        if not links:
            print("💡 Нет ссылок для скачивания.")
            return

        print(f"\n📥 Начинаю скачивание {len(links)} файлов...\n")
        start_time = time.time()

        for i, url in enumerate(links, 1):
            parsed = urlparse(url)
            filename = self._sanitize_filename(os.path.basename(parsed.path))

            progress = f"[{i:3d}/{len(links)}]"
            display_name = filename[:45] + "..." if len(filename) > 48 else filename
            print(f"{progress} {display_name}", end=" ", flush=True)

            success = self.download_file(url, filename, skip_existing)

            if i < len(links):
                time.sleep(self.request_delay)

        elapsed = time.time() - start_time
        self._print_report(elapsed)
        self._save_report(links_file)

    def _print_report(self, elapsed_seconds: float):
        print(f"\n{'=' * 70}")
        print(f"📊 ОТЧЁТ")
        print(f"{'=' * 70}")

        total = self.stats['ok'] + self.stats['fail'] + self.stats['skipped']
        success_rate = (self.stats['ok'] / total * 100) if total > 0 else 0

        print(f"✅ Успешно:     {self.stats['ok']:4d} ({success_rate:.1f}%)")
        print(f"⏭️ Пропущено:   {self.stats['skipped']:4d}")
        print(f"❌ Ошибки:      {self.stats['fail']:4d}")
        print(f"📦 Всего:       {total:4d}")
        print(f"💾 Скачано:     {self.stats['total_bytes'] / (1024 * 1024):.2f} MB")
        print(f"⏱️ Время:        {elapsed_seconds:.1f}с ({elapsed_seconds / 60:.1f} мин)")
        if total > 0:
            avg_speed = self.stats['total_bytes'] / elapsed_seconds / 1024
            print(f"🚀 Скорость:    {avg_speed:.1f} KB/s")
        print(f"📁 Папка:       {self.output_dir.absolute()}")
        print(f"{'=' * 70}")

    def _save_report(self, source_file: str):
        report_path = self.output_dir / "download_report.txt"
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(f"VWTS.RU Download Report\n")
                f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Source: {source_file}\n")
                f.write(f"Output: {self.output_dir.absolute()}\n")
                f.write("-" * 70 + "\n\n")
                f.write(f"Statistics:\n")
                f.write(f"  Successful:  {self.stats['ok']}\n")
                f.write(f"  Skipped:     {self.stats['skipped']}\n")
                f.write(f"  Failed:      {self.stats['fail']}\n")
                f.write(f"  Total size:  {self.stats['total_bytes'] / (1024 * 1024):.2f} MB\n")
            self._log(f"Отчёт: {report_path}", 'debug')
        except Exception as e:
            self._log(f"Не удалось сохранить отчёт: {e}", 'warning')


def main():
    parser = argparse.ArgumentParser(
        description='📥 Скачивание PDF с vwts.ru',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Примеры:
  %(prog)s links.txt
  %(prog)s links.txt -o docs -d 5
  %(prog)s links.txt --skip-existing -v
        '''
    )
    parser.add_argument('links_file', help='Файл со списком PDF-ссылок')
    parser.add_argument('-o', '--output', default=DEFAULT_OUTPUT_DIR,
                        help=f'Папка (по умолчанию: {DEFAULT_OUTPUT_DIR})')
    parser.add_argument('-d', '--delay', type=float, default=DEFAULT_REQUEST_DELAY,
                        help=f'Задержка в секундах (по умолчанию: {DEFAULT_REQUEST_DELAY})')
    parser.add_argument('--skip-existing', action='store_true',
                        help='Пропускать скачанные файлы')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Подробный вывод')

    args = parser.parse_args()

    print("📥 VWTS.RU PDF Downloader")
    print("-" * 70)

    downloader = VWTSDownloader(
        output_dir=args.output,
        request_delay=args.delay,
        verbose=args.verbose
    )

    downloader.run(args.links_file, skip_existing=args.skip_existing)
    print("\n✨ Готово!")


if __name__ == "__main__":
    # pip install requests
    main()