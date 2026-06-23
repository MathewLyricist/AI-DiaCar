#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI DiaCar - Сканер папок с мануалами
Находит все автомобили в папках и сохраняет в файл
"""

import os
import re
import csv
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict


class ManualScanner:
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.found_cars = []
        self.unrecognized_files = []
        self.statistics = defaultdict(int)

        # Маппинг брендов
        self.brand_mapping = {
            'ACURA': 'Acura', 'AUDI': 'Audi', 'BMW': 'BMW',
            'CHEVROLET': 'Chevrolet', 'CHRYSLER': 'Chrysler',
            'DAEWOO': 'Daewoo', 'FORD': 'Ford', 'HONDA': 'Honda',
            'MAN': 'MAN', 'MAZDA': 'Mazda', 'MITSUBISHI': 'Mitsubishi',
            'NISSAN': 'Nissan', 'OPEL': 'Opel', 'SUBARU': 'Subaru',
            'SUZUKI': 'Suzuki', 'TOYOTA': 'Toyota', 'LEXUS': 'Lexus',
            'VOLKSWAGEN': 'Volkswagen', 'VW': 'Volkswagen',
            'SKODA': 'Skoda', 'SEAT': 'Seat', 'ВАЗ': 'ВАЗ',
            'ГАЗ': 'ГАЗ', 'УАЗ': 'УАЗ', 'БЕЛАЗ': 'БЕЛАЗ',
            'КРАЗ': 'КРАЗ', 'КАМАЗ': 'КАМАЗ', 'РАЗНОЕ': 'Разное',
        }

        # Известные модели для распознавания
        self.known_models = {
            'Toyota': ['Camry', 'Corolla', 'RAV4', 'Land Cruiser', 'Prado',
                       'Mark II', 'Chaser', 'Cresta', 'Crown', 'Avalon',
                       'Prius', 'Highlander', '4Runner', 'Tacoma', 'Yaris',
                       'Auris', 'Avensis', 'Sienna', 'Sequoia', 'Supra', 'Celica'],
            'Lexus': ['RX', 'ES', 'IS', 'GS', 'LS', 'NX', 'GX', 'LX', 'UX', 'RC', 'LC'],
            'BMW': ['1 Series', '3 Series', '5 Series', '7 Series',
                    'X1', 'X3', 'X5', 'X6', 'X7', 'Z4', 'M3', 'M5'],
            'Chevrolet': ['Aveo', 'Camaro', 'Captiva', 'Cobalt', 'Cruze',
                          'Lanos', 'Lumina', 'Tahoe', 'Corvette', 'Spark',
                          'Tracker', 'TrailBlazer', 'Malibu', 'Niva', 'Lacetti'],
            'Volkswagen': ['Golf', 'Passat', 'Polo', 'Jetta', 'Tiguan',
                           'Touareg', 'Amarok', 'Atlas', 'Transporter',
                           'Scirocco', 'Sharan', 'Touran', 'CC', 'Beetle'],
            'Audi': ['A1', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8',
                     'Q2', 'Q3', 'Q5', 'Q7', 'Q8', 'TT', 'R8', 'e-tron'],
            'Skoda': ['Fabia', 'Octavia', 'Rapid', 'Kodiaq', 'Karoq', 'Superb', 'Yeti', 'Roomster'],
            'Mercedes-Benz': ['C-Class', 'E-Class', 'S-Class', 'A-Class',
                              'B-Class', 'CLA', 'GLA', 'GLC', 'GLE', 'GLS'],
            'Ford': ['Focus', 'Mondeo', 'Fiesta', 'Kuga', 'EcoSport',
                     'Explorer', 'Mustang', 'Ranger', 'Transit', 'Fusion', 'Edge'],
            'Honda': ['Accord', 'Civic', 'CR-V', 'HR-V', 'Pilot',
                      'Odyssey', 'Fit', 'Jazz', 'Ridgeline', 'CR-Z'],
            'Nissan': ['Qashqai', 'X-Trail', 'Patrol', 'Pathfinder',
                       'Juke', 'Note', 'Murano', 'Titan', 'Altima', 'Maxima',
                       'Navara', 'Terrano', 'Tiida', 'Sentra'],
            'Mazda': ['CX-5', 'CX-7', 'CX-9', 'Mazda3', 'Mazda6',
                      'CX-3', 'MX-5', 'BT-50', 'Tribute', 'CX-30'],
            'Mitsubishi': ['Outlander', 'Pajero', 'Lancer', 'ASX',
                           'Galant', 'Colt', 'Carisma', 'Grandis', 'Pajero Sport'],
            'Subaru': ['Forester', 'Outback', 'Impreza', 'Legacy',
                       'XV', 'Crosstrek', 'WRX', 'BRZ', 'Tribeca'],
            'Suzuki': ['Grand Vitara', 'Swift', 'SX4', 'Vitara',
                       'Jimny', 'Ignis', 'Baleno', 'Kizashi', 'Celerio'],
            'Hyundai': ['Solaris', 'Creta', 'Tucson', 'Santa Fe',
                        'Elantra', 'Sonata', 'Accent', 'Genesis', 'i30', 'ix35'],
            'Kia': ['Rio', 'Sportage', 'Sorento', 'Optima', 'Ceed',
                    'Picanto', 'Stonic', 'Niro', 'Stinger', 'Cerato', 'Mohave'],
            'Renault': ['Logan', 'Duster', 'Kaptur', 'Megane',
                        'Sandero', 'Fluence', 'Koleos', 'Arkana', 'Captur'],
            'Peugeot': ['308', '3008', '408', '508', '2008',
                        '5008', 'Partner', 'Bipper', '207', '307'],
            'Citroen': ['C4', 'C5', 'C3', 'C1', 'Berlingo',
                        'C4 Picasso', 'DS3', 'DS4', 'DS5', 'C4 Aircross'],
            'Opel': ['Astra', 'Insignia', 'Mokka', 'Corsa',
                     'Zafira', 'Meriva', 'Antara', 'Frontera', 'Vectra'],
            'ВАЗ': ['Priora', 'Kalina', 'Granta', 'Vesta',
                    'XRAY', 'Niva', 'Largus', 'Samara', 'Oka'],
        }

    def scan_directories(self):
        """Сканирование всех папок"""
        print("\n" + "=" * 70)
        print("🔍 AI DiaCar - СКАНИРОВАНИЕ ПАПЕК С МАНАУЛАМИ")
        print("=" * 70)
        print(f"📁 Путь: {self.base_path}")
        print(f"⏰ Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)

        if not self.base_path.exists():
            print(f"\n❌ ОШИБКА: Папка не найдена: {self.base_path}")
            print("💡 Проверьте путь в переменной BASE_PATH")
            return False

        brand_folders = [d for d in self.base_path.iterdir() if d.is_dir()]
        print(f"\n📁 Найдено папок брендов: {len(brand_folders)}")

        for brand_folder in sorted(brand_folders):
            brand = self._get_brand_name(brand_folder.name)
            print(f"\n{'─' * 70}")
            print(f"🚗 {brand_folder.name} → {brand}")
            print(f"{'─' * 70}")

            count = self._scan_brand_folder(brand_folder, brand)
            self.statistics[brand] = count

        return True

    def _get_brand_name(self, folder_name: str) -> str:
        """Получение имени бренда"""
        upper_name = folder_name.upper()

        if upper_name in self.brand_mapping:
            return self.brand_mapping[upper_name]
        if 'VAG' in upper_name or 'VOLKSWAGEN' in upper_name:
            return 'Volkswagen'
        if 'TOYOTA' in upper_name and 'LEXUS' in upper_name:
            return 'Toyota/Lexus'
        if 'Caterpillar' in folder_name or 'CAT' in upper_name:
            return 'Caterpillar'
        if 'РЕМОНТ' in upper_name and 'ДВИГАТЕЛЕЙ' in upper_name:
            return 'Caterpillar'

        return folder_name.title()

    def _scan_brand_folder(self, folder: Path, brand: str) -> int:
        """Сканирование папки бренда"""
        files_count = 0

        for file_path in folder.rglob('*'):
            if file_path.suffix.lower() in ['.pdf', '.djvu', '.djv']:
                self._process_file(file_path, brand)
                files_count += 1

        return files_count

    def _process_file(self, file_path: Path, brand: str):
        """Обработка файла"""
        rel_path = file_path.relative_to(self.base_path.parent)
        path_str = str(rel_path).replace('\\', '/')
        parent_folder = file_path.parent.name

        car_info = self._extract_info(file_path, brand, parent_folder)

        if car_info and car_info.get('model'):
            car_info['manual_path'] = path_str
            car_info['file_name'] = file_path.name
            car_info['folder'] = parent_folder
            self.found_cars.append(car_info)

            if len(self.found_cars) % 50 == 0:
                print(f"  → Обработано файлов: {len(self.found_cars)}")
        else:
            self.unrecognized_files.append({
                'path': path_str,
                'brand': brand,
                'file': file_path.name,
                'folder': parent_folder
            })

    def _extract_info(self, file_path: Path, brand: str, parent_folder: str) -> dict:
        """Извлечение информации из файла"""
        file_name = file_path.stem
        search_text = f"{file_name} {parent_folder}".lower()

        info = {
            'brand': brand,
            'model': None,
            'year': None,
            'typeEngine': None,
            'capacity': None,
            'transmission': None,
            'equipment': None,
            'generation': None
        }

        # 1. Извлечение года
        year_patterns = [
            r'\b(19|20)\d{2}\b',
            r'\b(\d{4})[-–](\d{4}|\d{2})\b',
        ]

        for pattern in year_patterns:
            year_match = re.search(pattern, search_text)
            if year_match:
                year_str = year_match.group(0)
                year_num = re.search(r'\d{4}', year_str)
                if year_num:
                    info['year'] = int(year_num.group())
                    break

        # 2. Извлечение модели (из известных)
        if brand in self.known_models:
            for model in sorted(self.known_models[brand], key=len, reverse=True):
                if re.search(r'\b' + re.escape(model.lower()) + r'\b', search_text):
                    info['model'] = model
                    break

        # 3. Если не найдена - пробуем извлечь из имени
        if not info['model']:
            # Ищем слова с заглавной буквы
            model_match = re.search(r'\b([A-Z][a-z]+)\b', file_name)
            if model_match:
                candidate = model_match.group(1)
                if not re.search(r'^(manual|service|guide|book|pdf|djvu|vol)', candidate.lower()):
                    info['model'] = candidate

        # 4. Поколение (E39, W210, Mk1, X90)
        gen_patterns = [
            r'\b([A-Z]\d{2,3})\b',
            r'\b(Mk\d+)\b',
        ]

        for pattern in gen_patterns:
            gen_match = re.search(pattern, search_text, re.I)
            if gen_match:
                info['generation'] = gen_match.group(1).upper()
                break

        # 5. Объем двигателя
        cap_patterns = [
            r'\b(\d\.?\d?)\s*[Ll]\b',
            r'\b(\d{3,4})\s*cc\b',
        ]

        for pattern in cap_patterns:
            cap_match = re.search(pattern, search_text)
            if cap_match:
                cap_value = cap_match.group(1)
                if 'L' in cap_match.group(0).upper():
                    info['capacity'] = int(float(cap_value) * 1000)
                else:
                    info['capacity'] = int(cap_value)
                break

        # 6. Тип двигателя
        engine_match = re.search(r'\b([A-Z]\d[A-Z]?-[A-Z0-9]+)\b', search_text, re.I)
        if engine_match:
            info['typeEngine'] = engine_match.group(1).upper()

        # 7. Если модель так и не найдена - используем имя папки
        if not info['model']:
            clean_name = re.sub(r'(VAG|manual|service|\d{4}[-–]?\d*)', '', parent_folder, flags=re.I)
            clean_name = re.sub(r'[-_\s]+', ' ', clean_name).strip()
            if clean_name and len(clean_name) > 2:
                info['model'] = clean_name.split()[0].capitalize()
            else:
                info['model'] = 'Unknown'

        return info

    def save_to_csv(self, output_file: str = 'found_cars.csv'):
        """Сохранение в CSV"""
        if not self.found_cars:
            print("\n⚠️  Нет данных для сохранения")
            return

        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['brand', 'model', 'year', 'typeEngine', 'capacity',
                          'transmission', 'equipment', 'generation', 'manual_path', 'file_name', 'folder']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.found_cars)

        print(f"\n✅ CSV сохранен: {output_file}")
        print(f"   Записей: {len(self.found_cars)}")

    def save_to_sql(self, output_file: str = 'found_cars.sql'):
        """Сохранение в SQL формат"""
        if not self.found_cars:
            print("\n⚠️  Нет данных для сохранения")
            return

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("-- AI DiaCar - Найденные автомобили\n")
            f.write(f"-- Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"-- Записей: {len(self.found_cars)}\n\n")
            f.write("USE car_manuals;\n\n")
            f.write("START TRANSACTION;\n\n")

            for i, car in enumerate(self.found_cars):
                if i % 100 == 0 and i > 0:
                    f.write(f"\n-- Batch {i // 100}\n")

                if car.get('model') and car['model'] != 'Unknown':
                    sql = self._make_insert(car)
                    f.write(sql + "\n")

            f.write("\nCOMMIT;\n")
            f.write(f"\n-- Всего записей: {len(self.found_cars)}\n")

        size = os.path.getsize(output_file) / 1024
        print(f"✅ SQL сохранен: {output_file} ({size:.1f} KB)")

    def _make_insert(self, car: dict) -> str:
        """Создание INSERT запроса"""
        brand = car['brand'].replace("'", "''")
        model = car.get('model', 'Unknown').replace("'", "''")
        year = car.get('year') if car.get('year') else 'NULL'
        engine = f"'{car['typeEngine']}'" if car.get('typeEngine') else 'NULL'
        capacity = car.get('capacity') if car.get('capacity') else 'NULL'
        transmission = f"'{car['transmission']}'" if car.get('transmission') else 'NULL'
        equipment = f"'{car['equipment']}'" if car.get('equipment') else 'NULL'
        generation = f"'{car['generation']}'" if car.get('generation') else 'NULL'
        path = f"'{car['manual_path']}'" if car.get('manual_path') else 'NULL'

        return f"""INSERT INTO cars (brand, model, year, typeEngine, capacity, transmission, equipment, generation, manual_path) VALUES ('{brand}', '{model}', {year}, {engine}, {capacity}, {transmission}, {equipment}, {generation}, {path});"""

    def save_unrecognized(self, output_file: str = 'unrecognized_files.csv'):
        """Сохранение нераспознанных файлов"""
        if not self.unrecognized_files:
            print(f"✅ Нераспознанных файлов: 0")
            return

        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['brand', 'folder', 'file_name', 'path']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.unrecognized_files)

        print(f"✅ Отчет: {output_file} ({len(self.unrecognized_files)} файлов)")

    def save_statistics(self, output_file: str = 'scan_statistics.json'):
        """Сохранение статистики"""
        # Группировка по брендам и моделям
        brand_models = defaultdict(lambda: defaultdict(int))
        years_count = defaultdict(int)

        for car in self.found_cars:
            brand = car['brand']
            model = car.get('model', 'Unknown')
            brand_models[brand][model] += 1

            if car.get('year'):
                years_count[car['year']] += 1

        stats = {
            'total_files': len(self.found_cars),
            'unrecognized_files': len(self.unrecognized_files),
            'by_brand': {brand: len(models) for brand, models in brand_models.items()},
            'by_brand_models': {brand: dict(models) for brand, models in brand_models.items()},
            'by_year': dict(sorted(years_count.items())),
            'generated': datetime.now().isoformat()
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)

        print(f"✅ Статистика: {output_file}")

    def print_stats(self):
        """Вывод статистики"""
        print("\n" + "=" * 70)
        print("📊 СТАТИСТИКА СКАНИРОВАНИЯ")
        print("=" * 70)
        print(f"📄 Всего найдено файлов: {len(self.found_cars)}")
        print(f"✅ Распознано автомобилей: {len([c for c in self.found_cars if c.get('model') != 'Unknown'])}")
        print(f"❌ Не распознано файлов: {len(self.unrecognized_files)}")

        # Уникальные модели по брендам
        unique_models = defaultdict(set)
        for car in self.found_cars:
            if car.get('model') and car['model'] != 'Unknown':
                unique_models[car['brand']].add(car['model'])

        print("\n📈 Уникальные модели по брендам:")
        for brand in sorted(unique_models.keys()):
            models = unique_models[brand]
            count = len(models)
            bar = '█' * (count // 2)
            print(f"  {brand:20s} {count:4d} моделей {bar}")

        # По годам
        years = [car['year'] for car in self.found_cars if car.get('year')]
        if years:
            print(f"\n📅 Годы: {min(years)} - {max(years)}")
            year_counts = defaultdict(int)
            for year in years:
                year_counts[year] += 1
            top_years = sorted(year_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            print("   Топ-5 годов:")
            for year, count in top_years:
                print(f"     {year}: {count} файлов")


def main():
    # ========== НАСТРОЙТЕ ПУТЬ ==========
    BASE_PATH = "/home/mathew/Политех/4-й курс/ВКР/ Project/AI DiaCar/AIModel/DataPDF/"
    # ====================================

    scanner = ManualScanner(BASE_PATH)

    if scanner.scan_directories():
        # Сохраняем результаты
        scanner.save_to_csv('found_cars.csv')
        scanner.save_to_sql('found_cars.sql')
        scanner.save_unrecognized('unrecognized_files.csv')
        scanner.save_statistics('scan_statistics.json')
        scanner.print_stats()

        print("\n" + "=" * 70)
        print("✅ СКАНИРОВАНИЕ ЗАВЕРШЕНО!")
        print("=" * 70)
        print("\n📁 Созданные файлы:")
        print("  1. found_cars.csv - ВСЕ найденные автомобили (CSV)")
        print("  2. found_cars.sql - SQL для импорта в БД")
        print("  3. unrecognized_files.csv - нераспознанные файлы")
        print("  4. scan_statistics.json - подробная статистика")
        print("\n💡 Следующие шаги:")
        print("  1. Откройте found_cars.csv и проверьте данные")
        print("  2. Отредактируйте при необходимости")
        print("  3. Импортируйте в БД:")
        print("     mysql -u root -p car_manuals < found_cars.sql")
        print("=" * 70 + "\n")
    else:
        print("\n❌ ОШИБКА: Не удалось просканировать папку")


if __name__ == "__main__":
    main()