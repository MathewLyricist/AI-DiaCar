#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Парсер руководств с drivetrend.ru
Имена файлов формируются по модели автомобиля (например: Acura_CSX_2008.pdf)
"""

import requests
from bs4 import BeautifulSoup
import os
import time
import re
from urllib.parse import urljoin, urlparse
import logging

# =============================================================================
# НАСТРОЙКИ
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('parser.log', encoding='utf-8', mode='a'),
        logging.StreamHandler()
    ]
)

BASE_URL = "https://drivetrend.ru/"
MANUALS_PAGE_URL = urljoin(BASE_URL, "avto-manuals/")
DOWNLOAD_DIR = "../downloads_drivetrend"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'ru-RU,ru;q=0.9',
    'Connection': 'keep-alive',
}

os.makedirs(DOWNLOAD_DIR, exist_ok=True)


# =============================================================================
# ФУНКЦИИ
# =============================================================================

def get_soup(url, session=None):
    """Загружает страницу и возвращает BeautifulSoup."""
    try:
        req_session = session if session else requests
        response = req_session.get(url, headers=HEADERS, timeout=20, allow_redirects=True)
        response.raise_for_status()
        response.encoding = 'utf-8'
        return BeautifulSoup(response.text, 'html.parser')
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка загрузки {url}: {e}")
        return None


def extract_car_model(manual_name, brand_name):
    """
    Извлекает модель и год из названия руководства для имени файла.
    Примеры:
      'Service Manual Acura CSX 2008' + 'ACURA' -> 'CSX_2008'
      'Audi 80 AVANT 1991' + 'AUDI' -> '80_AVANT_1991'
    """
    # Приводим к строке и убираем лишние пробелы
    text = str(manual_name).strip()
    brand = str(brand_name).strip().upper()

    # 1. Убираем служебные слова
    skip_words = ['service', 'manual', 'workshop', 'repair', 'handbook', 'guide',
                  'руководство', 'по', 'ремонту', 'эксплуатации', 'сервисное']
    for word in skip_words:
        text = re.sub(r'\b' + re.escape(word) + r'\b', '', text, flags=re.IGNORECASE)

    # 2. Убираем название бренда из текста (чтобы не дублировалось)
    # Разбиваем бренд на слова (например, "TOYOTA (LEXUS)" -> ["TOYOTA", "LEXUS"])
    brand_parts = re.findall(r'\w+', brand)
    for part in brand_parts:
        if len(part) > 1:  # не убираем одиночные буквы
            text = re.sub(r'\b' + re.escape(part) + r'\b', '', text, flags=re.IGNORECASE)

    # 3. Очищаем от лишних пробелов и спецсимволов
    text = ' '.join(text.split())
    text = re.sub(r'[^\w\s\-]', '', text)  # оставляем буквы, цифры, пробелы, дефисы

    # 4. Если что-то осталось — используем, иначе берем оригинальное название
    if text.strip():
        model_part = text.strip()
    else:
        model_part = manual_name.strip()

    # 5. Заменяем пробелы на подчёркивания для имени файла
    filename_safe = re.sub(r'\s+', '_', model_part)
    filename_safe = re.sub(r'_+', '_', filename_safe)  # убираем дубли _
    filename_safe = filename_safe.strip('_')

    # 6. Добавляем расширение .pdf
    if not filename_safe.lower().endswith('.pdf'):
        filename_safe += '.pdf'

    return filename_safe


def extract_brands_and_manuals(soup):
    """Извлекает руководства по маркам."""
    manuals_by_brand = {}
    if not soup:
        return manuals_by_brand

    brand_headers = soup.find_all(['h2', 'h3'], string=True)

    for header in brand_headers:
        brand_name = header.get_text(strip=True).upper()
        if not brand_name or len(brand_name) > 30 or any(
                skip in brand_name.lower() for skip in
                ['поиск', 'рубрик', 'свежие', 'содержанию', 'популярное', 'марка автомобиля']
        ):
            continue

        logging.info(f"Найден бренд: {brand_name}")
        manuals = []
        next_table = header.find_next('table')
        if not next_table:
            continue

        rows = next_table.find_all('tr')
        for row in rows[1:]:
            cols = row.find_all('td')
            if len(cols) >= 1:
                title_cell = cols[0]
                title_link = title_cell.find('a')
                if title_link and title_link.get('href'):
                    manual_name = title_link.get_text(strip=True)
                    manual_page_url = urljoin(BASE_URL, title_link.get('href'))
                    manuals.append({'name': manual_name, 'page_url': manual_page_url})

        if manuals:
            manuals_by_brand[brand_name] = manuals

    return manuals_by_brand


def get_download_url_with_wpdmdl(page_url, session=None):
    """Извлекает URL скачивания через wpdmdl + 302 redirect."""
    try:
        soup = get_soup(page_url, session)
        if not soup:
            return None

        wpdmdl_id = None

        # Стратегия 1: data-wpdmdl
        for tag in soup.find_all(attrs={'data-wpdmdl': True}):
            val = tag.get('data-wpdmdl')
            if isinstance(val, list):
                val = ' '.join(val)
            if val and str(val).strip().isdigit():
                wpdmdl_id = str(val).strip()
                break

        # Стратегия 2: другие data-атрибуты
        if not wpdmdl_id:
            for attr in ['data-id', 'data-download-id', 'data-file-id']:
                for tag in soup.find_all(attrs={attr: True}):
                    val = tag.get(attr)
                    if isinstance(val, list):
                        val = ' '.join(val)
                    if val and str(val).strip().isdigit():
                        wpdmdl_id = str(val).strip()
                        break
                if wpdmdl_id:
                    break

        # Стратегия 3: JS-переменные
        if not wpdmdl_id:
            for script in soup.find_all('script', string=True):
                if script.string:
                    match = re.search(r'wpdmdl["\']?\s*[:=]\s*["\']?(\d+)', script.string, re.I)
                    if match:
                        wpdmdl_id = match.group(1)
                        break

        # Стратегия 4: body class postid-XXXX
        if not wpdmdl_id:
            body = soup.find('body')
            if body and body.get('class'):
                classes = body.get('class')
                if isinstance(classes, list):
                    for cls in classes:
                        match = re.match(r'postid-(\d+)', str(cls))
                        if match:
                            wpdmdl_id = match.group(1)
                            break

        if not wpdmdl_id:
            logging.warning(f"⚠ Не найден wpdmdl: {page_url}")
            return None

        refresh = f"{int(time.time())}{str(time.time()).split('.')[1][:5]}"
        download_url = f"{page_url.rstrip('/')}?wpdmdl={wpdmdl_id}&refresh={refresh}"
        logging.info(f"✓ URL: {download_url}")
        return download_url

    except Exception as e:
        logging.error(f"❌ Ошибка извлечения wpdmdl: {e}")
        return None


def download_file(page_url, brand_name, manual_name, downloaded_urls, session=None):
    """Скачивает файл с именем на основе модели автомобиля."""
    if not page_url or page_url in downloaded_urls:
        return

    logging.info(f"  📄 {manual_name}")
    download_url = get_download_url_with_wpdmdl(page_url, session)
    if not download_url:
        logging.warning("  ⚠ Пропущено: не найден wpdmdl")
        return

    # 🔥 Формируем имя файла на основе модели
    filename = extract_car_model(manual_name, brand_name)

    safe_brand = "".join(c for c in brand_name if c.isalnum() or c in (' ', '-', '_')).strip()
    brand_dir = os.path.join(DOWNLOAD_DIR, safe_brand)
    os.makedirs(brand_dir, exist_ok=True)

    try:
        req_session = session if session else requests
        response = req_session.get(
            download_url,
            headers=HEADERS,
            stream=True,
            timeout=60,
            allow_redirects=True
        )
        response.raise_for_status()

        # Проверка Content-Type
        content_type = response.headers.get('Content-Type', '').lower()
        if 'text/html' in content_type:
            logging.warning(f"  ⚠ Получен HTML вместо файла")
            return

        file_path = os.path.join(brand_dir, filename)

        # Проверка: файл уже существует
        if os.path.exists(file_path) and os.path.getsize(file_path) > 1024:
            logging.info(f"  ✓ Уже существует: {filename}")
            downloaded_urls.add(page_url)
            return

        # Скачивание
        logging.info(f"  ⬇ Скачивание: {filename}")
        size = 0
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    size += len(chunk)

        if size < 1024:
            logging.warning(f"  ⚠ Файл мал ({size} б)")
            if os.path.exists(file_path):
                os.remove(file_path)
            return

        # Валидация PDF
        if filename.lower().endswith('.pdf'):
            with open(file_path, 'rb') as f:
                if not f.read(5).startswith(b'%PDF'):
                    logging.warning(f"  ⚠ Не валидный PDF: {file_path}")
                    os.rename(file_path, file_path + '.html')
                    return

        logging.info(f"  ✓ Скачан: {filename} ({size} б)")
        downloaded_urls.add(page_url)

    except Exception as e:
        logging.error(f"  ❌ Ошибка: {e}")
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)


def main():
    logging.info(f"🚀 Запуск парсера drivetrend.ru")
    session = requests.Session()
    session.headers.update(HEADERS)

    soup = get_soup(MANUALS_PAGE_URL, session)
    if not soup:
        logging.error("❌ Не удалось загрузить страницу")
        return

    logging.info("🔍 Извлечение руководств...")
    manuals_by_brand = extract_brands_and_manuals(soup)

    if not manuals_by_brand:
        logging.warning("⚠ Не найдено руководств")
        return

    downloaded_urls = set()
    success = 0
    total = sum(len(m) for m in manuals_by_brand.values())

    logging.info(f"📊 Найдено: {len(manuals_by_brand)} марок, {total} руководств")

    for brand, manuals in manuals_by_brand.items():
        logging.info(f"\n📁 {brand} ({len(manuals)})")
        for manual in manuals:
            before = len(downloaded_urls)
            download_file(manual['page_url'], brand, manual['name'], downloaded_urls, session)
            if len(downloaded_urls) > before:
                success += 1
            time.sleep(2)
        time.sleep(3)

    logging.info(f"\n✅ Готово! Скачано: {success}/{total}")
    logging.info(f"📂 Папка: {os.path.abspath(DOWNLOAD_DIR)}")


if __name__ == "__main__":
    main()