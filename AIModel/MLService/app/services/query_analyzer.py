import re
from typing import Dict, List
from app.utils.text_normalizer import normalize_word
from app.utils.russian_dictionary import AUTOMOTIVE_SYNONYMS

class QueryAnalyzer:
    STOP_WORDS = {'как', 'что', 'где', 'когда', 'почему', 'зачем', 'если', 'то', 'и', 'в', 'на', 'не', 'для', 'же', 'бы', 'ли'}

    def analyze(self, query: str) -> Dict:
        query_lower = query.lower()
        raw_words = re.findall(r'[а-яА-Яa-zA-Z]+', query_lower)
        words = [w for w in raw_words if len(w) > 2 and w not in self.STOP_WORDS]

        normalized = [normalize_word(w) for w in words]
        keywords = list(dict.fromkeys(normalized))

        expanded = set(keywords)
        for kw in keywords:
            for key, syns in AUTOMOTIVE_SYNONYMS.items():
                if kw == key or kw in syns or key in kw:
                    expanded.add(key)
                    expanded.update(syns)
        if 'грм' in keywords or 'ремень' in keywords:
            expanded.add('ремень')
            expanded.add('ремень грм')
            expanded.add('замена')
        if 'кулис' in keywords:
            expanded.add('кулиса')
        if 'регулиров' in keywords:
            expanded.add('регулировка')

        keywords = list(expanded)

        question_type = self._detect_question_type(query_lower)
        return {
            'original_query': query,
            'keywords': keywords,
            'question_type': question_type,
        }

    def _detect_question_type(self, query: str) -> str:
        if any(w in query for w in ['регулиров', 'настройк', 'отрегулирова']):
            return 'adjustment'
        elif any(w in query for w in ['замен', 'смен', 'помен', 'установк']):
            return 'replacement'
        elif any(w in query for w in ['почему', 'причина', 'не работает', 'глохн']):
            return 'diagnosis'
        else:
            return 'general'