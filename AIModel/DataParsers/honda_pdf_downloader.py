import os
import re
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# Настройки
BASE_URL = "https://hondaworld.ru/documentation.htm"
DOWNLOAD_FOLDER = "honda_pdfs"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://hondaworld.ru/"
}


def create_download_folder(folder_name):
    """Создаёт папку для загрузок, если её нет"""
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        print(f"✓ Создана папка: {folder_name}")
    return folder_name


def get_pdf_links(page_url):
    """Парсит страницу и возвращает список ссылок на PDF"""
    try:
        response = requests.get(page_url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        pdf_links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            # Проверяем, что ссылка ведёт на PDF
            if href.lower().endswith('.pdf'):
                full_url = urljoin(page_url, href)
                text = link.get_text(strip=True) or "Без названия"
                # Очищаем имя файла от лишних символов
                pdf_links.append({'url': full_url, 'name': text})

        return pdf_links
    except requests.RequestException as e:
        print(f"✗ Ошибка при загрузке страницы: {e}")
        return []


def sanitize_filename(filename, max_length=150):
    """Очищает имя файла от недопустимых символов"""
    # Удаляем опасные символы для путей в ОС
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Обрезаем, если слишком длинное
    if len(sanitized) > max_length:
        name, ext = os.path.splitext(sanitized)
        sanitized = name[:max_length - len(ext)] + ext
    return sanitized.strip()


def download_file(url, filename, folder):
    """Скачивает файл с прогресс-баром"""
    filepath = os.path.join(folder, filename)

    # Если файл уже есть — пропускаем
    if os.path.exists(filepath):
        print(f"⊘ Уже скачан: {filename}")
        return True

    try:
        with requests.get(url, headers=HEADERS, stream=True, timeout=30) as r:
            r.raise_for_status()
            total = int(r.headers.get('content-length', 0))

            with open(filepath, 'wb') as f:
                downloaded = 0
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        # Прогресс-бар
                        if total:
                            percent = downloaded / total * 100
                            print(f"\r  ↓ {filename}: {percent:.1f}%", end='', flush=True)
            print(f"\r✓ Скачан: {filename} ({downloaded / 1024 / 1024:.2f} МБ)")
            return True
    except requests.RequestException as e:
        print(f"\n✗ Ошибка при скачивании {filename}: {e}")
        # Удаляем битый файл, если он создался
        if os.path.exists(filepath):
            os.remove(filepath)
        return False


def main():
    print(f"🔍 Анализ страницы: {BASE_URL}\n")

    # 1. Создаём папку
    folder = create_download_folder(DOWNLOAD_FOLDER)

    # 2. Получаем ссылки
    pdfs = get_pdf_links(BASE_URL)
    if not pdfs:
        print("⚠ PDF-файлы не найдены на странице")
        return

    print(f"✓ Найдено PDF-файлов: {len(pdfs)}\n")

    # 3. Скачиваем
    success = 0
    for i, item in enumerate(pdfs, 1):
        print(f"[{i}/{len(pdfs)}] Обработка: {item['name'][:60]}...")

        # Формируем безопасное имя файла
        clean_name = sanitize_filename(f"{item['name']}.pdf")

        if download_file(item['url'], clean_name, folder):
            success += 1

        # Небольшая пауза, чтобы не перегружать сервер
        time.sleep(1)

    # Итог
    print(f"\n📊 Готово! Скачано: {success} из {len(pdfs)} файлов")
    print(f"📁 Путь к файлам: {os.path.abspath(folder)}")


if __name__ == "__main__":
    main()