#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 VWTS.RU Link Extractor
Извлекает PDF-ссылки из vwts_models.json или URL страницы

Использование:
    python vwts_links_extractor.py vwts_models.json -o pdf_links.txt
    python vwts_links_extractor.py https://vwts.ru/vw_sharan_7n.html -o links.txt
"""

import os, re, json, time, argparse
from pathlib import Path
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,*/*;q=0.8',
    'Accept-Language': 'ru-RU,ru;q=0.9',
    'Referer': 'https://vwts.ru/',
}


class VWTSLinkExtractor:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.stats = {'total': 0, 'by_category': {}}

    def _detect_category(self, filename: str, title: str) -> str:
        text = (filename + ' ' + title).lower()
        if any(k in text for k in ['engine', 'двигател', 'motor']):
            return 'engines'
        elif any(k in text for k in ['electr', 'wiring', 'electro', 'электро']):
            return 'electrical'
        elif any(k in text for k in ['brake', 'tormoz', 'abs']):
            return 'brakes'
        elif any(k in text for k in ['fuel', 'topliv', 'injection']):
            return 'fuel_system'
        elif any(k in text for k in ['gearbox', 'transmission', 'кпп', 'dsg']):
            return 'transmission'
        elif any(k in text for k in ['body', 'кузов', 'interior', 'exterior']):
            return 'body'
        elif any(k in text for k in ['suspension', 'steering', 'подвеск', 'рулев']):
            return 'suspension'
        elif any(k in text for k in ['cooling', 'heating', 'conditioner', 'охлажд', 'кондиц']):
            return 'climate'
        elif any(k in text for k in ['maintenance', 'сервис', 'repair']):
            return 'maintenance'
        elif any(k in text for k in ['owner', 'manual', 'руководств', 'pps_']):
            return 'general'
        else:
            return 'other'

    def extract_from_json(self, json_file: str) -> list:
        """Извлечение ссылок из vwts_models.json"""
        all_links = []

        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                models = json.load(f)

            print(f"📋 Загружено моделей из JSON: {len(models)}")

            for i, model in enumerate(models, 1):
                model_url = model.get('url') or model.get('pdf_page_url')
                model_name = model.get('model_name', 'Unknown')
                brand = model.get('brand', 'Unknown')

                if not model_url:
                    continue

                print(f"\n[{i}/{len(models)}] {brand} — {model_name[:40]}")
                links = self.extract_from_url(model_url)

                for link in links:
                    link['brand'] = brand
                    link['model'] = model_name

                all_links.extend(links)
                time.sleep(2)

        except FileNotFoundError:
            print(f"❌ Файл не найден: {json_file}")
        except json.JSONDecodeError as e:
            print(f"❌ Ошибка JSON: {e}")
        except Exception as e:
            print(f"❌ Ошибка: {e}")

        return all_links

    def extract_from_url(self, page_url: str) -> list:
        """Извлечение PDF-ссылок со страницы"""
        try:
            print(f"📥 Загрузка: {page_url}")
            resp = self.session.get(page_url, timeout=30)
            resp.raise_for_status()

            soup = BeautifulSoup(resp.text, 'html.parser')
            links = []
            seen = set()

            for a in soup.find_all('a', href=True):
                href = a['href'].strip()

                if not href.lower().endswith('.pdf'):
                    continue
                if 'vwts.ru' not in href and not href.startswith('/'):
                    continue

                full_url = f"https://vwts.ru{href}" if href.startswith('/') else href

                if full_url in seen:
                    continue
                seen.add(full_url)

                filename = os.path.basename(urlparse(full_url).path)
                title = a.get_text(strip=True) or filename
                title = re.sub(r'\s+', ' ', title).strip()
                category = self._detect_category(filename, title)

                links.append({
                    'url': full_url,
                    'filename': filename,
                    'title': title[:100],
                    'category': category
                })

                self.stats['total'] += 1
                self.stats['by_category'][category] = self.stats['by_category'].get(category, 0) + 1

            print(f"   ✅ Найдено PDF: {len(links)}")
            return links

        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
            return []

    def save_links(self, links: list, output_file: str, format: str = 'simple'):
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if format == 'simple':
            with open(output_path, 'w', encoding='utf-8') as f:
                for link in links:
                    f.write(f"{link['url']}\n")

        elif format == 'detailed':
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"# VWTS.RU PDF Links\n")
                f.write(f"# Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"# Total: {len(links)}\n")
                f.write("#" + "=" * 70 + "\n\n")
                for link in links:
                    f.write(f"# [{link.get('brand', 'N/A')}] [{link['category']}] {link['title']}\n")
                    f.write(f"{link['url']}\n\n")

        elif format == 'csv':
            with open(output_path, 'w', encoding='utf-8', newline='') as f:
                f.write("URL,Filename,Title,Category,Brand,Model\n")
                for link in links:
                    title = link['title'].replace('"', '""')
                    f.write(f'"{link["url"]}","{link["filename"]}","{title}",'
                            f'"{link["category"]}","{link.get("brand", "")}","{link.get("model", "")}"\n')

        print(f"\n💾 Сохранено: {output_path.absolute()}")

    def print_stats(self):
        print(f"\n{'=' * 60}")
        print(f"📊 СТАТИСТИКА")
        print(f"{'=' * 60}")
        print(f"Всего ссылок: {self.stats['total']}")
        if self.stats['by_category']:
            print(f"\nПо категориям:")
            for cat, count in sorted(self.stats['by_category'].items(), key=lambda x: -x[1]):
                print(f"   • {cat}: {count}")
        print(f"{'=' * 60}")


def main():
    parser = argparse.ArgumentParser(
        description='🔍 Извлечение PDF-ссылок с vwts.ru',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Примеры:
  %(prog)s vwts_models.json -o pdf_links.txt
  %(prog)s https://vwts.ru/vw_sharan_7n.html -o sharan.txt
  %(prog)s vwts_models.json --format csv -o links.csv
        '''
    )
    parser.add_argument('source', help='JSON файл или URL страницы')
    parser.add_argument('-o', '--output', default='pdf_links.txt',
                        help='Файл для сохранения (по умолчанию: pdf_links.txt)')
    parser.add_argument('--format', choices=['simple', 'detailed', 'csv'], default='simple',
                        help='Формат вывода (по умолчанию: simple)')

    args = parser.parse_args()

    print("🔍 VWTS.RU Link Extractor")
    print("-" * 60)

    extractor = VWTSLinkExtractor()
    all_links = []

    if args.source.startswith('http'):
        links = extractor.extract_from_url(args.source)
        all_links.extend(links)
    elif args.source.endswith('.json'):
        all_links = extractor.extract_from_json(args.source)
    else:
        print("❌ Укажите JSON файл или URL")
        return

    if all_links:
        extractor.save_links(all_links, args.output, args.format)
        extractor.print_stats()
        print(f"\n✨ Готово! Скачайте файлы:")
        print(f"   python vwts_downloader.py {args.output}")
    else:
        print("\n❌ Не найдено ни одной ссылки.")


if __name__ == "__main__":
    # pip install requests beautifulsoup4
    main()