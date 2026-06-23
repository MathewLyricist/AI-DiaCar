#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📁 VWTS.RU File Organizer v2.0
Улучшенная версия с расширенным сопоставлением моделей
"""
import os, re, sys, json, shutil, argparse
from pathlib import Path
from urllib.parse import urlparse, unquote
from collections import defaultdict

DEFAULT_OUTPUT_DIR = "vwts_sorted"
SUPPORTED_EXTENSIONS = ['.pdf']


class VWTSFileOrganizer:
    def __init__(self, models_json: str, source_dir: str, output_dir: str):
        self.models_file = Path(models_json)
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir)
        self.stats = {'total': 0, 'sorted': 0, 'unsorted': 0, 'errors': 0}
        self.model_map = {}
        self.file_map = {}
        self.models_list = []  # Сохраняем все модели для поиска

    def load_models(self) -> dict:
        try:
            with open(self.models_file, 'r', encoding='utf-8') as f:
                models = json.load(f)
            print(f"📋 Загружено моделей: {len(models)}")

            self.models_list = models

            for model in models:
                url = model.get('url') or model.get('pdf_page_url', '')
                if url:
                    url = url.rstrip('/')
                    self.model_map[url] = {
                        'brand': model.get('brand', 'Unknown'),
                        'model_name': model.get('model_name', 'Unknown'),
                        'model_code': model.get('model_code', ''),
                        'folder_name': self._create_folder_name(model),
                        'year_from': model.get('year_from', 0),
                        'year_to': model.get('year_to', 9999)
                    }
            print(f"✅ Создана карта моделей: {len(self.model_map)} записей")
            return self.model_map
        except FileNotFoundError:
            print(f"❌ Файл не найден: {self.models_file}")
            return {}
        except json.JSONDecodeError as e:
            print(f"❌ Ошибка JSON: {e}")
            return {}

    def _create_folder_name(self, model: dict) -> str:
        brand = model.get('brand', 'Unknown')
        model_name = model.get('model_name', 'Unknown')
        folder_name = f"{brand} {model_name}"
        folder_name = re.sub(r'[<>:"/\\|?*]', '_', folder_name)
        folder_name = re.sub(r'_+', '_', folder_name)
        return folder_name.strip('_. ')[:150]

    def _extract_filename_from_url(self, url: str) -> str:
        parsed = urlparse(url)
        filename = os.path.basename(parsed.path)
        return unquote(filename)

    def _build_file_to_url_map(self, pdf_urls_file: str = None):
        if pdf_urls_file and Path(pdf_urls_file).exists():
            try:
                with open(pdf_urls_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and line.startswith('http') and '.pdf' in line:
                            filename = self._extract_filename_from_url(line)
                            self.file_map[filename.lower()] = line
                print(f"📄 Загружено ссылок на PDF: {len(self.file_map)}")
            except Exception as e:
                print(f"⚠️ Не удалось загрузить файл ссылок: {e}")

    def _extract_year_from_filename(self, filename: str) -> int:
        """Извлечение года из имени файла"""
        year_match = re.search(r'(19|20)\d{2}', filename)
        if year_match:
            return int(year_match.group())
        return 0

    def find_model_for_file(self, filename: str) -> dict | None:
        """Улучшенный поиск модели с приоритетами"""
        filename_lower = filename.lower()
        file_year = self._extract_year_from_filename(filename)

        # Расширенные коды моделей
        model_codes = {
            'sharan': ['sharan', '7n1', '7n2', '7n'],
            'passat_b2': ['passat', 'b2', '32b'],
            'passat_b3': ['passat', 'b3', '3a'],
            'passat_b4': ['passat', 'b4', '3a2'],
            'passat_b5': ['passat', 'b5', '3b'],
            'passat_b6': ['passat', 'b6', '3c'],
            'passat_b7': ['passat', 'b7', '36'],
            'passat_b8': ['passat', 'b8', '3g'],
            'golf_1': ['golf', '1', 'mk1', '17'],
            'golf_2': ['golf', '2', 'mk2', '19e', '1g'],
            'golf_3': ['golf', '3', 'mk3', '1h'],
            'golf_4': ['golf', '4', 'mk4', '1j'],
            'golf_5': ['golf', '5', 'mk5', '1k'],
            'golf_6': ['golf', '6', 'mk6', '5k'],
            'golf_7': ['golf', '7', 'mk7', '5g', 'au'],
            'golf_8': ['golf', '8', 'mk8', 'cd'],
            'jetta_1': ['jetta', '1', 'mk1'],
            'jetta_2': ['jetta', '2', 'mk2'],
            'jetta_3': ['jetta', '3', 'mk3', '1h'],
            'jetta_4': ['jetta', '4', 'mk4', '1j'],
            'jetta_5': ['jetta', '5', 'mk5', '1k'],
            'jetta_6': ['jetta', '6', 'mk6', '5k'],
            'tiguan_1': ['tiguan', '1', '5n'],
            'tiguan_2': ['tiguan', '2', 'ad1', 'bw'],
            'touareg_1': ['touareg', '1', '7l'],
            'touareg_2': ['touareg', '2', '7p'],
            'touareg_3': ['touareg', '3', 'cr'],
            'polo_2': ['polo', '2', '86c'],
            'polo_3': ['polo', '3', '6n', '6kv'],
            'polo_4': ['polo', '4', '9n'],
            'polo_5': ['polo', '5', '6r', 'aw'],
            'polo_6': ['polo', '6', 'az'],
            'polo_sedan': ['polo', 'sedan', '612'],
            'audi_a3_1': ['a3', '8l'],
            'audi_a3_2': ['a3', '8p'],
            'audi_a3_3': ['a3', '8v'],
            'audi_a3_4': ['a3', '8y'],
            'audi_a4_b5': ['a4', 'b5', '8d'],
            'audi_a4_b6': ['a4', 'b6', '8e'],
            'audi_a4_b7': ['a4', 'b7', '8e'],
            'audi_a4_b8': ['a4', 'b8', '8k'],
            'audi_a4_b9': ['a4', 'b9', '8w'],
            'audi_a6_c4': ['a6', 'c4', '4a'],
            'audi_a6_c5': ['a6', 'c5', '4b'],
            'audi_a6_c6': ['a6', 'c6', '4f'],
            'audi_a6_c7': ['a6', 'c7', '4g'],
            'audi_a6_c8': ['a6', 'c8', '4k'],
            'audi_a8_d2': ['a8', 'd2', '4d'],
            'audi_a8_d3': ['a8', 'd3', '4e'],
            'audi_a8_d4': ['a8', 'd4', '4h'],
            'audi_q5_1': ['q5', '8r'],
            'audi_q5_2': ['q5', 'fy'],
            'audi_q7_1': ['q7', '4l'],
            'audi_q7_2': ['q7', '4m'],
            'skoda_octavia_1': ['octavia', '1u'],
            'skoda_octavia_2': ['octavia', '1z'],
            'skoda_octavia_3': ['octavia', '5e'],
            'skoda_octavia_4': ['octavia', 'nx'],
            'skoda_fabia_1': ['fabia', '6y'],
            'skoda_fabia_2': ['fabia', '5j'],
            'skoda_fabia_3': ['fabia', 'nj'],
            'skoda_kodiaq': ['kodiaq', 'ns'],
            'skoda_kodiaq_2': ['kodiaq', '2'],
            'skoda_superb_1': ['superb', '3u'],
            'skoda_superb_2': ['superb', '3t'],
            'skoda_superb_3': ['superb', '3v'],
            'skoda_yeti': ['yeti', '5l'],
            'skoda_karoq': ['karoq', 'nu'],
            'skoda_scala': ['scala', 'nw'],
            'skoda_kamiq': ['kamiq', 'nw'],
            'seat_ibiza_1': ['ibiza', '6k'],
            'seat_ibiza_2': ['ibiza', '6l'],
            'seat_ibiza_3': ['ibiza', '6j'],
            'seat_ibiza_4': ['ibiza', 'kj'],
            'seat_leon_1': ['leon', '1m'],
            'seat_leon_2': ['leon', '1p'],
            'seat_leon_3': ['leon', '5f'],
            'seat_leon_4': ['leon', 'kl'],
            'seat_alhambra_1': ['alhambra', '710'],
            'seat_alhambra_2': ['alhambra', '711'],
            'seat_toledo_1': ['toledo', '1l'],
            'seat_toledo_2': ['toledo', '1m'],
            'seat_toledo_3': ['toledo', '5p'],
            'seat_toledo_4': ['toledo', 'kg'],
            'vw_t2': ['t2', 'transporter', 'bus'],
            'vw_t3': ['t3', 'transporter', '25'],
            'vw_t4': ['t4', 'transporter', '70', 'eurovan'],
            'vw_t5': ['t5', 'transporter', '7h'],
            'vw_t6': ['t6', 'transporter', 'sg'],
            'vw_t_cross': ['t-cross', 'tcross', 'c1'],
            'vw_t_roc': ['t-roc', 'troc', 'a1'],
            'vw_sportsvan': ['sportsvan', 'touran sport'],
            'vw_taos': ['taos'],
            'vw_up': ['up!', 'up', 'aa'],
            'vw_e_up': ['e-up', 'eup'],
            'vw_lupo': ['lupo', '6x', '6e'],
            'vw_beetle': ['beetle', 'cabrio', 'cabriolet'],
            'vw_eos': ['eos', '1f'],
            'vw_scirocco': ['scirocco', '13', '137'],
            'vw_phateon': ['phaeton', '3d'],
            'vw_arteon': ['arteon', '3h'],
            'vw_atlas': ['atlas', 'ca1'],
            'vw_id3': ['id.3', 'id3', 'e1'],
            'vw_id4': ['id.4', 'id4', 'e2'],
            'vw_id5': ['id.5', 'id5'],
            'vw_id7': ['id.7', 'id7'],
            'vw_amarok': ['amarok', '2h', 's1'],
            'vw_caddy_1': ['caddy', '14d'],
            'vw_caddy_2': ['caddy', '2k', '9k'],
            'vw_caddy_3': ['caddy', '2k'],
            'vw_caddy_4': ['caddy', 'sa', 'sb'],
            'vw_caddy_5': ['caddy', 'sk'],
            'vw_touran_1': ['touran', '1t'],
            'vw_touran_2': ['touran', '5t'],
            'vw_sharan_1': ['sharan', '7n'],
            'vw_sharan_2': ['sharan', '7n2'],
        }

        # ПРИОРИТЕТ 1: Поиск по кодам моделей с учётом года
        best_match = None
        best_score = 0

        for model_key, codes in model_codes.items():
            matches = sum(1 for code in codes if code in filename_lower)
            if matches >= 1:
                # Ищем соответствующую модель в model_map
                for model_url, model_info in self.model_map.items():
                    folder_lower = model_info['folder_name'].lower().replace(' ', '').replace('_', '')
                    model_key_clean = model_key.replace('_', '')

                    if model_key_clean in folder_lower or model_key.replace('_', ' ') in model_info[
                        'folder_name'].lower():
                        # Проверка по году
                        year_match = True
                        if file_year > 0:
                            if model_info.get('year_from', 0) > 0 and file_year < model_info['year_from']:
                                year_match = False
                            if model_info.get('year_to', 9999) < 9999 and file_year > model_info['year_to']:
                                year_match = False

                        if year_match and matches > best_score:
                            best_score = matches
                            best_match = model_info

        if best_match:
            return best_match

        # ПРИОРИТЕТ 2: Поиск по file_map (если есть ссылки)
        if filename_lower in self.file_map:
            pdf_url = self.file_map[filename_lower]
            for model_url, model_info in self.model_map.items():
                if model_url in pdf_url:
                    return model_info

        # ПРИОРИТЕТ 3: Поиск по названию модели (3+ совпадения)
        for model_url, model_info in self.model_map.items():
            model_name_lower = model_info['model_name'].lower()
            keywords = re.findall(r'[a-zA-Z0-9]+', model_name_lower)
            keywords = [k for k in keywords if len(k) > 2]
            matches = sum(1 for k in keywords if k in filename_lower)
            if matches >= 3:
                return model_info

        return None

    def scan_pdf_files(self) -> list:
        pdf_files = []
        if not self.source_dir.exists():
            print(f"❌ Папка не найдена: {self.source_dir}")
            return []
        print(f"🔍 Сканирование: {self.source_dir}")
        for ext in SUPPORTED_EXTENSIONS:
            pdf_files.extend(self.source_dir.glob(f"*{ext}"))
            pdf_files.extend(self.source_dir.glob(f"*{ext.upper()}"))
        pdf_files = sorted(set(pdf_files), key=lambda x: x.name.lower())
        print(f"✅ Найдено PDF файлов: {len(pdf_files)}")
        return pdf_files

    def organize_files(self, pdf_urls_file: str = None, copy_mode: bool = False):
        self.load_models()
        if not self.model_map:
            print("💡 Нет данных о моделях. Прерываю.")
            return

        if pdf_urls_file:
            self._build_file_to_url_map(pdf_urls_file)

        self.output_dir.mkdir(parents=True, exist_ok=True)
        pdf_files = self.scan_pdf_files()
        if not pdf_files:
            print("💡 Нет PDF файлов для сортировки.")
            return

        print(f"\n📁 Начинаю сортировку {len(pdf_files)} файлов...\n")
        self.stats['total'] = len(pdf_files)
        unsorted_files = []

        for i, src_file in enumerate(pdf_files, 1):
            filename = src_file.name
            print(f"[{i:4d}/{len(pdf_files)}] {filename[:60]}", end=" ")

            model_info = self.find_model_for_file(filename)
            if model_info:
                model_folder = self.output_dir / model_info['folder_name']
                model_folder.mkdir(parents=True, exist_ok=True)
                dst_file = model_folder / filename
                try:
                    if copy_mode:
                        shutil.copy2(src_file, dst_file)
                    else:
                        shutil.move(str(src_file), str(dst_file))
                    print(f"→ {model_info['folder_name'][:35]} ✅")
                    self.stats['sorted'] += 1
                except Exception as e:
                    print(f"❌ Ошибка: {e}")
                    self.stats['errors'] += 1
            else:
                print("→ ❌ Не найдена модель")
                unsorted_files.append(filename)
                self.stats['unsorted'] += 1

        if unsorted_files:
            unsorted_folder = self.output_dir / "_UNSORTED"
            unsorted_folder.mkdir(exist_ok=True)
            print(f"\n⚠️ {len(unsorted_files)} файлов не отсортировано:")
            for filename in unsorted_files[:10]:
                print(f"   • {filename}")
            if len(unsorted_files) > 10:
                print(f"   ... и ещё {len(unsorted_files) - 10}")

            for filename in unsorted_files:
                src = self.source_dir / filename
                dst = unsorted_folder / filename
                if src.exists():
                    try:
                        if copy_mode:
                            shutil.copy2(src, dst)
                        else:
                            shutil.move(str(src), str(dst))
                    except Exception as e:
                        print(f"   ❌ Ошибка перемещения {filename}: {e}")

        self._save_report(unsorted_files)
        self._print_summary()

    def _print_summary(self):
        print(f"\n{'=' * 70}")
        print(f"📊 ОТЧЁТ О СОРТИРОВКЕ")
        print(f"{'=' * 70}")
        print(f"📦 Всего файлов:    {self.stats['total']}")
        print(
            f"✅ Отсортировано:   {self.stats['sorted']} ({self.stats['sorted'] / max(self.stats['total'], 1) * 100:.1f}%)")
        print(f"⚠️ Не найдено модель: {self.stats['unsorted']}")
        print(f"❌ Ошибки:          {self.stats['errors']}")
        print(f"📁 Папка:           {self.output_dir.absolute()}")

        model_folders = [d for d in self.output_dir.iterdir() if d.is_dir() and not d.name.startswith('_')]
        if model_folders:
            print(f"\n📂 Создано папок моделей: {len(model_folders)}")
            print(f"   Примеры:")
            for folder in sorted(model_folders)[:5]:
                file_count = len(list(folder.glob('*.pdf')))
                print(f"   • {folder.name}: {file_count} файлов")
            if len(model_folders) > 5:
                print(f"   ... и ещё {len(model_folders) - 5} папок")
        print(f"{'=' * 70}")

    def _save_report(self, unsorted_files: list):
        report_path = self.output_dir / "organize_report.txt"
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(f"VWTS.RU File Organization Report\n")
                f.write(f"Generated: {__import__('time').strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Source: {self.source_dir.absolute()}\n")
                f.write(f"Output: {self.output_dir.absolute()}\n")
                f.write(f"Models JSON: {self.models_file.absolute()}\n")
                f.write("-" * 70 + "\n")
                f.write(f"Statistics:\n")
                f.write(f"  Total files:     {self.stats['total']}\n")
                f.write(f"  Sorted:          {self.stats['sorted']}\n")
                f.write(f"  Unsorted:        {self.stats['unsorted']}\n")
                f.write(f"  Errors:          {self.stats['errors']}\n")
                if unsorted_files:
                    f.write(f"\nUnsorted files ({len(unsorted_files)}):\n")
                    for filename in unsorted_files:
                        f.write(f"  • {filename}\n")
            print(f"📝 Отчёт сохранён: {report_path}")
        except Exception as e:
            print(f"⚠️ Не удалось сохранить отчёт: {e}")


def main():
    parser = argparse.ArgumentParser(
        description='📁 Сортировка PDF файлов vwts.ru по моделям',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('models_json', help='Файл vwts_models.json')
    parser.add_argument('source_dir', help='Папка с PDF файлами')
    parser.add_argument('-o', '--output', default=DEFAULT_OUTPUT_DIR,
                        help=f'Папка для отсортированных файлов (по умолчанию: {DEFAULT_OUTPUT_DIR})')
    parser.add_argument('--copy', action='store_true',
                        help='Копировать файлы вместо перемещения')
    parser.add_argument('--links', type=str, metavar='FILE',
                        help='Файл со списком PDF-ссылок (для точного сопоставления)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Тестовый режим (без реального перемещения)')
    args = parser.parse_args()

    print("📁 VWTS.RU File Organizer v2.0")
    print("-" * 70)

    organizer = VWTSFileOrganizer(
        models_json=args.models_json,
        source_dir=args.source_dir,
        output_dir=args.output
    )

    if args.dry_run:
        print("🔍 РЕЖИМ ПРОВЕРКИ (файлы не будут перемещены)")
        print("-" * 70)
        organizer.load_models()
        pdf_files = organizer.scan_pdf_files()
        print(f"\n📋 Будет отсортировано {len(pdf_files)} файлов")
        print(f"📁 В папку: {Path(args.output).absolute()}")
    else:
        organizer.organize_files(pdf_urls_file=args.links, copy_mode=args.copy)
        print("\n✨ Готово!")


if __name__ == "__main__":
    main()