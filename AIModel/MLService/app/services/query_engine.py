import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class QueryEngine:

    def __init__(self):
        self.llm = None
        self.qa_chain = None

    def initialize(self):
        logger.info("✅ QueryEngine инициализирован (без векторного поиска)")

    def process_query(self, query: str, car_info: Optional[Dict] = None) -> Dict:
        return {
            "answer": "Контекст должен передаваться из бэкенда",
            "sources": [],
            "suggested_pages": [],
            "clarification_questions": self._generate_clarification_questions(query, [])
        }

    def _generate_clarification_questions(self, query: str, search_results: List[Dict]) -> List[str]:
        questions = []
        query_lower = query.lower()

        if any(word in query_lower for word in ['двигатель', 'мотор', 'заводится']):
            questions.append("Какие именно симптомы наблюдаются при запуске двигателя?")
            questions.append("Есть ли посторонние звуки или индикаторы на панели?")

        if any(word in query_lower for word in ['тормоз', 'торможение', 'педаль']):
            questions.append("При каких условиях проявляется проблема с тормозами?")
            questions.append("Педаль тормоза мягкая или твёрдая?")

        if any(word in query_lower for word in ['коробка', 'передача', 'кпп']):
            questions.append("Проблема проявляется при переключении всех передач или конкретных?")

        if not questions:
            questions.append("Когда впервые появилась эта проблема?")
            questions.append("При каких условиях проблема проявляется сильнее?")

        return questions[:2]