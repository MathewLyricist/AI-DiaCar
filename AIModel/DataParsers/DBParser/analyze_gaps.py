#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Анализ имеющихся мануалов и поиск недостающих популярных моделей
"""

import csv
import json
from collections import defaultdict
from datetime import datetime


class ManualAnalyzer:
    def __init__(self):
        self.existing_cars = set()  # Уникальные авто (brand+model+year+generation)
        self.existing_data = []  # Все данные из CSV
        self.general_manuals = set()  # Общие мануалы
        self.missing_popular = []  # Популярные но отсутствующие

        # Популярные модели по брендам (для поиска пробелов)
        self.popular_models = {
            'Toyota': [
                ('Camry', [2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020]),
                ('Corolla', [2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020]),
                ('RAV4', [2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020]),
                ('Land Cruiser Prado',
                 [2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019,
                  2020]),
                ('Highlander', [2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020]),
                ('Prius', [2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016]),
            ],
            'Lexus': [
                ('RX',
                 [2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019,
                  2020]),
                ('ES', [2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018]),
                ('IS', [2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017]),
                ('GS', [2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017]),
                ('NX', [2014, 2015, 2016, 2017, 2018, 2019, 2020]),
            ],
            'BMW': [
                ('3 Series',
                 [2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019]),
                ('5 Series',
                 [2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018]),
                ('X5',
                 [2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018]),
                ('X3',
                 [2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018]),
                ('X6', [2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019]),
            ],
            'Mercedes-Benz': [
                ('C-Class', [2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020]),
                ('E-Class', [2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016]),
                ('S-Class', [2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018]),
                ('GLC', [2015, 2016, 2017, 2018, 2019, 2020]),
                ('GLE', [2015, 2016, 2017, 2018, 2019, 2020]),
            ],
            'Audi': [
                ('A4', [2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019]),
                ('A6', [2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018]),
                ('Q5', [2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020]),
                ('Q7', [2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018]),
                ('A3', [2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016]),
            ],
            'Hyundai': [
                ('Solaris', [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020]),
                ('Creta', [2016, 2017, 2018, 2019, 2020, 2021]),
                ('Tucson', [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020]),
                ('Santa Fe', [2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018]),
                ('Sonata', [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020]),
            ],
            'Kia': [
                ('Rio', [2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020]),
                ('Sportage', [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020]),
                ('Sorento', [2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020]),
                ('Optima', [2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020]),
                ('Ceed', [2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018]),
            ],
            'Ford': [
                ('Focus', [2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019]),
                ('Mondeo', [2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018]),
                ('Kuga', [2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019]),
                ('Explorer', [2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020]),
                ('Fusion', [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019]),
            ],
            'Nissan': [
                ('Qashqai', [2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020]),
                ('X-Trail', [2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020]),
                ('Patrol', [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020]),
                ('Note', [2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017]),
                ('Murano', [2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015]),
            ],
            'Mazda': [
                ('CX-5', [2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020]),
                ('Mazda3',
                 [2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018]),
                ('Mazda6',
                 [2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017]),
                ('CX-7', [2006, 2007, 2008, 2009, 2010, 2011, 2012]),
                ('CX-9', [2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016]),
            ],
            'Mitsubishi': [
                ('Outlander',
                 [2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020]),
                ('Pajero', [2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019]),
                ('Lancer', [2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017]),
                ('ASX', [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020]),
                ('Pajero Sport', [2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020]),
            ],
            'Honda': [
                ('Civic', [2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018]),
                ('Accord', [2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015]),
                ('CR-V',
                 [2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017,
                  2018]),
                ('Pilot', [2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016]),
                ('Fit', [2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014]),
            ],
            'Subaru': [
                ('Forester',
                 [2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018]),
                ('Outback',
                 [2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018]),
                ('Impreza', [2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016]),
                ('XV', [2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020]),
                ('Legacy', [2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014]),
            ],
            'Suzuki': [
                ('Grand Vitara', [2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015]),
                ('Swift', [2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017]),
                ('SX4', [2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016]),
                ('Jimny',
                 [1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014,
                  2015, 2016, 2017, 2018]),
                ('Vitara', [2015, 2016, 2017, 2018, 2019, 2020]),
            ],
            'Renault': [
                ('Logan', [2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018]),
                ('Duster', [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020]),
                ('Kaptur', [2016, 2017, 2018, 2019, 2020, 2021]),
                ('Megane', [2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016]),
                ('Sandero', [2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018]),
            ],
            'Peugeot': [
                ('308', [2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019]),
                ('3008', [2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020]),
                ('408', [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019]),
                ('508', [2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020]),
                ('2008', [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020]),
            ],
            'Citroen': [
                ('C4', [2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018]),
                ('C5',
                 [2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016]),
                ('C3',
                 [2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017]),
                ('C4 Aircross', [2012, 2013, 2014, 2015, 2016, 2017]),
                ('Berlingo', [2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018]),
            ],
            'Opel': [
                ('Astra', [2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018]),
                ('Insignia', [2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017]),
                ('Mokka', [2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019]),
                ('Corsa', [2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018]),
                ('Zafira', [2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017]),
            ],
            'Skoda': [
                ('Octavia',
                 [2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019]),
                ('Fabia',
                 [2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016,
                  2017, 2018]),
                ('Yeti', [2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017]),
                ('Rapid', [2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020]),
                ('Kodiaq', [2017, 2018, 2019, 2020, 2021]),
            ],
            'ВАЗ': [
                ('Priora', [2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018]),
                ('Kalina', [2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018]),
                ('Granta', [2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020]),
                ('Vesta', [2015, 2016, 2017, 2018, 2019, 2020, 2021]),
                ('Niva',
                 [2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016,
                  2017, 2018, 2019, 2020]),
                ('Largus', [2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020]),
            ],
            'ГАЗ': [
                ('Газель',
                 [2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019,
                  2020]),
                ('Газель NEXT', [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020]),
                ('Соболь', [2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020]),
                ('Волга', [1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010]),
            ],
        }

        # Популярные двигатели по брендам
        self.popular_engines = {
            'Toyota': ['1JZ-GE', '1JZ-GTE', '2JZ-GE', '2JZ-GTE', '1AZ-FE', '2AZ-FE', '2AR-FE', '1ZR-FE', '2ZR-FE',
                       '1GR-FE', '2GR-FE'],
            'BMW': ['N52B25', 'N52B30', 'N54B30', 'N55B30', 'N20B20', 'B48B20', 'S54B32', 'M54B25', 'M54B30'],
            'Mercedes-Benz': ['M271', 'M272', 'M273', 'M274', 'M276', 'OM642', 'OM651'],
            'Volkswagen': ['EA888', 'EA211', '1.8 TSI', '2.0 TSI', '1.4 TSI', '2.0 TDI', '1.9 TDI'],
            'Hyundai': ['G4FA', 'G4FC', 'G4KD', 'G4KE', 'D4FA', 'D4FB'],
            'Kia': ['G4FA', 'G4FC', 'G4KD', 'G4KE', 'D4FA', 'D4FB'],
            'Ford': ['Duratec', 'EcoBoost 1.6', 'EcoBoost 2.0', 'Duratorq TDCi'],
            'Nissan': ['HR16DE', 'MR20DE', 'QR20DE', 'QR25DE', 'VQ35DE', 'YD22DDTi'],
            'Mazda': ['L3-VE', 'L5-VE', 'PE-VPS', 'PY-VPS', 'R2', 'RF'],
            'Mitsubishi': ['4G63', '4G64', '4B11', '4B12', '6B31', '4D56', '4M41'],
            'Honda': ['R18A', 'R20A', 'K20A', 'K24A', 'L15A', 'N22A'],
            'Subaru': ['EJ20', 'EJ25', 'FB20', 'FB25', 'FA20', 'EE20'],
            'ВАЗ': ['21114', '21116', '21126', '21127', '21129', '11186'],
        }

    def load_existing_data(self, csv_file: str):
        """Загрузка имеющихся данных из CSV"""
        print(f"📊 Загрузка данных из {csv_file}...")

        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.existing_data.append(row)

                # Создаем уникальный ключ (исключаем общие мануалы)
                brand = row['brand'].strip()
                model = row['model'].strip()
                year = row['year'].strip() if row['year'] else ''
                generation = row['generation'].strip() if row['generation'] else ''

                # Пропускаем общие мануалы
                if self._is_general_manual(brand, model):
                    self.general_manuals.add(f"{brand}|{model}")
                    continue

                # Создаем ключ для уникальности
                key = f"{brand}|{model}|{year}|{generation}"
                self.existing_cars.add(key)

        print(f"✅ Загружено {len(self.existing_data)} записей")
        print(f"✅ Уникальных авто: {len(self.existing_cars)}")
        print(f"⚠️  Общих мануалов: {len(self.general_manuals)}")

    def _is_general_manual(self, brand: str, model: str) -> bool:
        """Проверка на общий мануал"""
        general_keywords = ['Common', 'General', 'Obschee', 'Общее', 'VAG', 'Electrical',
                            'Diagnostics', 'Transmission', 'Climate', 'Maintenance', 'Body',
                            'Chassis', 'Brake', 'Fuel', 'Engine', 'Tdi', 'Engines']

        brand_lower = brand.lower()
        model_lower = model.lower()

        for keyword in general_keywords:
            if keyword.lower() in brand_lower or keyword.lower() in model_lower:
                return True

        return False

    def find_missing_popular(self, output_file: str = 'missing_popular_cars.csv'):
        """Поиск популярных недостающих моделей"""
        print("\n🔍 Поиск недостающих популярных моделей...")

        missing = []

        for brand, models in self.popular_models.items():
            for model, years in models:
                for year in years:
                    # Проверяем наличие
                    key_pattern = f"{brand}|{model}|{year}|"
                    found = any(key_pattern in key for key in self.existing_cars)

                    if not found:
                        # Добавляем информацию о двигателях
                        engines = self.popular_engines.get(brand, ['Unknown'])

                        missing.append({
                            'brand': brand,
                            'model': model,
                            'year': year,
                            'engine_type': ', '.join(engines[:3]),  # Первые 3 популярных
                            'capacity': self._get_typical_capacity(brand, model),
                            'transmission': 'Manual, Automatic',
                            'equipment': 'Standard, Comfort, Luxe',
                            'generation': self._get_generation(brand, model, year),
                            'priority': self._get_priority(brand, model, year),
                            'manual_path': '',
                            'has_manual': 'FALSE',
                            'notes': f'Популярная модель в РФ'
                        })

        # Сохраняем
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['brand', 'model', 'year', 'engine_type', 'capacity',
                          'transmission', 'equipment', 'generation', 'priority',
                          'manual_path', 'has_manual', 'notes']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(missing)

        print(f"✅ Найдено {len(missing)} недостающих популярных моделей")
        print(f"💾 Сохранено в {output_file}")

        self.missing_popular = missing
        return missing

    def _get_typical_capacity(self, brand: str, model: str) -> str:
        """Типичные объемы двигателей"""
        capacities = {
            'Toyota': '1.6, 1.8, 2.0, 2.5, 3.5',
            'BMW': '1.6, 2.0, 2.5, 3.0, 4.4',
            'Mercedes-Benz': '1.6, 1.8, 2.0, 2.5, 3.0, 3.5',
            'Volkswagen': '1.4, 1.6, 1.8, 2.0',
            'Hyundai': '1.4, 1.6, 2.0, 2.4',
            'Kia': '1.4, 1.6, 2.0, 2.4',
            'Ford': '1.6, 1.8, 2.0, 2.3, 2.5',
            'Nissan': '1.6, 2.0, 2.5, 3.5',
            'ВАЗ': '1.6',
            'ГАЗ': '2.8, 2.9',
        }
        return capacities.get(brand, 'Unknown')

    def _get_generation(self, brand: str, model: str, year: int) -> str:
        """Поколение автомобиля"""
        generations = {
            'Toyota': {
                'Camry': {range(2006, 2012): 'XV40', range(2012, 2018): 'XV50', range(2018, 2024): 'XV70'},
                'Corolla': {range(2007, 2014): 'E140/E150', range(2014, 2020): 'E170'},
            },
            'BMW': {
                '3 Series': {range(2005, 2012): 'E90/E91', range(2012, 2019): 'F30/F31'},
                '5 Series': {range(2003, 2010): 'E60/E61', range(2010, 2017): 'F10/F11'},
            },
        }

        if brand in generations and model in generations[brand]:
            for year_range, gen in generations[brand][model].items():
                if year in year_range:
                    return gen

        return 'Unknown'

    def _get_priority(self, brand: str, model: str, year: int) -> str:
        """Приоритет поиска"""
        high_priority_brands = ['Toyota', 'Hyundai', 'Kia', 'Volkswagen', 'BMW', 'Mercedes-Benz']

        if brand in high_priority_brands and year >= 2010:
            return 'High'
        elif year >= 2005:
            return 'Medium'
        else:
            return 'Low'

    def generate_summary(self, output_file: str = 'analysis_summary.json'):
        """Генерация сводки анализа"""
        summary = {
            'existing': {
                'total_files': len(self.existing_data),
                'unique_cars': len(self.existing_cars),
                'general_manuals': len(self.general_manuals),
            },
            'missing': {
                'popular_models': len(self.missing_popular),
                'high_priority': len([m for m in self.missing_popular if m['priority'] == 'High']),
                'medium_priority': len([m for m in self.missing_popular if m['priority'] == 'Medium']),
                'low_priority': len([m for m in self.missing_popular if m['priority'] == 'Low']),
            },
            'by_brand': {},
            'generated': datetime.now().isoformat()
        }

        # Группировка по брендам
        brand_count = defaultdict(int)
        for car in self.existing_cars:
            brand = car.split('|')[0]
            brand_count[brand] += 1

        summary['by_brand'] = dict(brand_count)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        print(f"📄 Сводка сохранена в {output_file}")

    def print_statistics(self):
        """Вывод статистики"""
        print("\n" + "=" * 70)
        print("📊 СТАТИСТИКА АНАЛИЗА")
        print("=" * 70)
        print(f"📁 Всего файлов: {len(self.existing_data)}")
        print(f"🚗 Уникальных авто: {len(self.existing_cars)}")
        print(f"📚 Общих мануалов: {len(self.general_manuals)}")
        print(f"❌ Недостающих популярных: {len(self.missing_popular)}")

        # По приоритетам
        high = len([m for m in self.missing_popular if m['priority'] == 'High'])
        medium = len([m for m in self.missing_popular if m['priority'] == 'Medium'])
        low = len([m for m in self.missing_popular if m['priority'] == 'Low'])

        print(f"\n🎯 По приоритету:")
        print(f"   Высокий: {high}")
        print(f"   Средний: {medium}")
        print(f"   Низкий: {low}")

        # Топ брендов
        brand_count = defaultdict(int)
        for car in self.existing_cars:
            brand = car.split('|')[0]
            brand_count[brand] += 1

        print(f"\n📈 Топ брендов (имеющиеся):")
        for brand, count in sorted(brand_count.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"   {brand}: {count}")


def main():
    print("=" * 70)
    print("🔍 AI DiaCar - Анализ имеющихся и поиск недостающих мануалов")
    print("=" * 70)

    analyzer = ManualAnalyzer()

    # Загрузка имеющихся данных
    analyzer.load_existing_data('found_cars.csv')

    # Поиск недостающих
    analyzer.find_missing_popular('missing_popular_cars.csv')

    # Генерация сводки
    analyzer.generate_summary('analysis_summary.json')

    # Статистика
    analyzer.print_statistics()

    print("\n" + "=" * 70)
    print("✅ АНАЛИЗ ЗАВЕРШЕН")
    print("=" * 70)
    print("\n📁 Созданные файлы:")
    print("  1. missing_popular_cars.csv - Недостающие популярные модели")
    print("  2. analysis_summary.json - Сводка анализа")
    print("\n💡 Следующие шаги:")
    print("  1. Проверить missing_popular_cars.csv")
    print("  2. Найти мануалы для приоритетных моделей")
    print("  3. Добавить новые мануалы в папку DataPDF")
    print("  4. Запустить scan_manuals.py заново")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()