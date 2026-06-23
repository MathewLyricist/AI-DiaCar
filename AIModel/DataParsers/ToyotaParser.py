import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from pathlib import Path

# Настройки
BASE_URL = "https://toyota-rolf.ru/owners/manuals/"
OUTPUT_DIR = "toyota_manuals"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
TIMEOUT = 30
DELAY_BETWEEN_REQUESTS = 2  # секунды между запросами


def create_output_dir():
    """Создаёт папку для сохранения файлов"""
    Path(OUTPUT_DIR).mkdir(exist_ok=True)


def get_page_soup(url):
    """Получает и парсит HTML-страницу"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        response.raise_for_status()
        response.encoding = response.apparent_encoding  # корректная кодировка
        return BeautifulSoup(response.text, 'lxml')
    except requests.RequestException as e:
        print(f"❌ Ошибка при загрузке {url}: {e}")
        return None


def extract_manual_links(soup, base_url):
    """Извлекает ссылки на PDF с названием модели авто в имени файла"""
    manuals = []

    for link in soup.find_all('a', href=True):
        href = link['href']
        full_url = urljoin(base_url, href)

        if not full_url.lower().endswith('.pdf'):
            continue

        # 1. Ищем название модели: поднимаемся к ближайшему заголовку h3/h4
        model_name = None
        current = link
        for _ in range(10):  # ограничиваем глубину поиска
            prev_sibling = current.find_previous_sibling()
            if prev_sibling and prev_sibling.name in ['h3', 'h4', 'h5']:
                model_name = prev_sibling.get_text(strip=True)
                break
            if current.parent and current.parent.name in ['h3', 'h4', 'h5']:
                model_name = current.parent.get_text(strip=True)
                break
            current = current.parent
            if not current:
                break

        # 2. Текст описания документа
        doc_type = None
        for sibling in link.find_previous_siblings():
            text = sibling.get_text(strip=True)
            if text and 'скачать' not in text.lower() and len(text) > 5:
                doc_type = text
                break

        # 3. Формируем безопасное имя файла (ИСПРАВЛЕНО: генератор с 'for c in ...')
        def safe_filename(text, max_len=40):
            if not text:
                return ""
            # ✅ Правильный синтаксис генератора
            cleaned = "".join(c if c.isalnum() or c in '._- ' else '_' for c in str(text))
            cleaned = '_'.join(cleaned.split())  # заменяем пробелы на _
            return cleaned[:max_len].strip('_')

        model_clean = safe_filename(model_name, 30) or "Toyota"
        doc_clean = safe_filename(doc_type, 40) or "manual"

        filename = f"{model_clean}_{doc_clean}.pdf"
        # Убираем дубли подчёркиваний
        while '__' in filename:
            filename = filename.replace('__', '_')

        manuals.append({
            'url': full_url,
            'filename': filename,
            'title': f"{model_name or 'Toyota'} — {doc_type or 'Manual'}"
        })

    # Убираем дубликаты по URL и уникализируем имена файлов
    seen_urls = set()
    seen_filenames = {}
    result = []

    for m in manuals:
        if m['url'] in seen_urls:
            continue
        seen_urls.add(m['url'])

        fname = m['filename']
        if fname in seen_filenames:
            seen_filenames[fname] += 1
            name, ext = os.path.splitext(fname)
            fname = f"{name}_{seen_filenames[fname]}{ext}"
        else:
            seen_filenames[fname] = 0

        m['filename'] = fname
        result.append(m)

    return result


def download_file(url, filename):
    """Скачивает файл по ссылке с корректным определением размера"""
    try:
        filepath = os.path.join(OUTPUT_DIR, filename)

        # Если файл уже существует — пропускаем
        if os.path.exists(filepath):
            print(f"⏭️ Уже скачан: {filename}")
            return True

        # Сначала делаем HEAD-запрос для получения размера файла
        head_resp = requests.head(url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
        file_size = head_resp.headers.get('Content-Length')
        file_size_mb = f"{int(file_size) / 1024 / 1024:.2f} МБ" if file_size else "размер неизвестен"

        # Теперь скачиваем файл
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT, stream=True)
        response.raise_for_status()

        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:  # фильтр keep-alive chunks
                    f.write(chunk)

        # Получаем реальный размер сохранённого файла
        actual_size = os.path.getsize(filepath)
        print(f"✅ Скачан: {filename} ({actual_size / 1024 / 1024:.2f} МБ)")
        return True

    except requests.RequestException as e:
        print(f"❌ Ошибка скачивания {url}: {e}")
        return False
    except OSError as e:
        print(f"❌ Ошибка записи файла {filename}: {e}")
        return False


def main():
    print(f"🔍 Парсинг страницы: {BASE_URL}")
    create_output_dir()

    soup = get_page_soup(BASE_URL)
    if not soup:
        print("Не удалось загрузить страницу. Проверьте подключение и URL.")
        return

    manuals = extract_manual_links(soup, BASE_URL)
    print(f"📚 Найдено мануалов: {len(manuals)}\n")

    if not manuals:
        print("⚠️ Не найдено ссылок на PDF. Возможно, сайт использует JavaScript для подгрузки контента.")
        print("💡 Решение: используйте Selenium или Playwright для динамического парсинга.")
        return

    success_count = 0
    for i, manual in enumerate(manuals, 1):
        print(f"[{i}/{len(manuals)}] {manual['title'][:60]}...")
        if download_file(manual['url'], manual['filename']):
            success_count += 1
        time.sleep(DELAY_BETWEEN_REQUESTS)  # вежливая задержка

    print(f"\n🎉 Готово! Скачано: {success_count}/{len(manuals)} файлов в папку '{OUTPUT_DIR}'")


if __name__ == "__main__":
    main()