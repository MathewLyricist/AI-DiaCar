import json
import logging
from pathlib import Path
from typing import List, Dict, Optional

from app.config import settings
from app.utils.text_normalizer import normalize_word

logger = logging.getLogger(__name__)

class KnowledgeLoader:
    def __init__(self):
        self.specific = {}
        self.total_entries = 0
        self.root = Path(settings.JSON_KNOWLEDGE_PATH)
        if not self.root.exists():
            logger.warning(f"Директория JSON знаний не найдена: {self.root}")

    def _find_json_file_by_content(self, brand: str, model: str) -> Optional[Path]:
        brand_lower = brand.lower()
        model_lower = model.lower()
        brand_dir = self.root / brand_lower
        if not brand_dir.exists():
            for candidate in self.root.iterdir():
                if candidate.is_dir() and candidate.name.lower() == brand_lower:
                    brand_dir = candidate
                    break
        if not brand_dir.exists() or not brand_dir.is_dir():
            return None

        for json_file in brand_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                file_brand = data.get("brand", "")
                file_model = data.get("model", "")
                if (file_brand and file_brand.lower() == brand_lower and
                    file_model and file_model.lower() == model_lower):
                    logger.info(f"Найден JSON по содержимому: {json_file}")
                    return json_file
            except Exception as e:
                logger.debug(f"Ошибка чтения {json_file}: {e}")
                continue
        return None

    def _find_json_file(self, brand: str, model: str) -> Optional[Path]:
        brand_lower = brand.lower()
        model_lower = model.lower()
        patterns = [
            f"{brand_lower}/{model_lower}.json",
            f"{brand_lower}/{model_lower}_*.json",
            f"{brand_lower}/*{model_lower}*.json",
        ]
        for pattern in patterns:
            matches = list(self.root.glob(pattern))
            if matches:
                return matches[0]
        return None

    def _load_file(self, path: Path, brand: str, model: str):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            brand = data.get("brand", brand)
            model = data.get("model", model)
            year_from = data.get("year_from")
            year_to = data.get("year_to")

            entries = data.get("issues", [data])
            key = (brand.lower(), model.lower())
            self.specific.setdefault(key, [])
            for entry in entries:
                entry["brand"] = brand
                entry["model"] = model
                if year_from is not None:
                    entry["year_from"] = year_from
                if year_to is not None:
                    entry["year_to"] = year_to
                entry.setdefault("symptoms", [])
                entry.setdefault("tags", [])
                entry.setdefault("confidence", 0.5)
                entry.setdefault("manual_reference", None)
                self.specific[key].append(entry)
                self.total_entries += 1
            logger.info(f"Ленивая загрузка {len(entries)} записей для {brand}/{model} из {path.name}")
        except Exception as e:
            logger.error(f"Ошибка загрузки {path}: {e}")

    def _ensure_loaded(self, brand: str, model: str):
        if not brand or not model:
            return
        key = (brand.lower(), model.lower())
        if key in self.specific:
            return
        json_file = self._find_json_file(brand, model)
        print("json_file",json_file)
        if not json_file:
            json_file = self._find_json_file_by_content(brand, model)
        if json_file:
            self._load_file(json_file, brand, model)
        else:
            logger.warning(f"Не найден JSON для {brand}/{model}")

    def find(self, brand: str, model: str, keywords: List[str], year: int = None) -> Optional[Dict]:
        from app.utils.russian_dictionary import STOP_WORDS

        if not brand or not model:
            return None
        self._ensure_loaded(brand, model)

        key = (brand.lower(), model.lower())
        candidates = self.specific.get(key, [])
        if not candidates:
            return None

        query_terms = set()
        for kw in keywords:
            for word in kw.split():
                norm = normalize_word(word)
                if norm and len(norm) > 2 and norm not in STOP_WORDS:
                    query_terms.add(norm)
        if not query_terms:
            return None

        best_entry = None
        best_score = 0.0
        for entry in candidates:
            if year is not None:
                yf = entry.get("year_from")
                yt = entry.get("year_to")
                if yf is not None and yt is not None and not (yf <= year <= yt):
                    continue

            raw = entry.get("title", "").lower() + " "
            raw += " ".join(entry.get("tags", [])).lower() + " "
            raw += " ".join(entry.get("symptoms", [])).lower()
            entry_terms = set()
            for w in re.findall(r'[а-яё]+', raw):
                norm_w = normalize_word(w)
                if norm_w and len(norm_w) > 2 and norm_w not in STOP_WORDS:
                    entry_terms.add(norm_w)
            if not entry_terms:
                continue

            matched = len(query_terms & entry_terms)
            ratio = matched / len(query_terms)
            confidence = entry.get("confidence", 0.5)
            total_score = ratio * confidence
            if 'троит' in entry.get('tags', []) or 'глохнет' in entry.get('tags', []):
                total_score += 0.2
            if total_score > best_score:
                best_score = total_score
                best_entry = entry

        return best_entry if best_score >= 0.3 else None

    def get_entries(self, brand: str, model: str) -> List[Dict]:
        self._ensure_loaded(brand, model)
        key = (brand.lower(), model.lower())
        return self.specific.get(key, []).copy()

knowledge_loader = KnowledgeLoader()