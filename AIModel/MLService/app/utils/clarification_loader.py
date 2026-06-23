import json
import logging
from typing import List
from app.config import settings

logger = logging.getLogger(__name__)

class ClarificationLoader:
    def __init__(self):
        self.themes = []
        self.default_questions = []
        self._load()

    def _load(self):
        path = settings.CLARIFICATION_QUESTIONS_PATH
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.themes = data.get("themes", [])
            self.default_questions = data.get("default", [])
            logger.info(f"Загружено {len(self.themes)} тем уточняющих вопросов")
        except Exception as e:
            logger.error(f"Ошибка загрузки {path}: {e}")
            self.themes = []
            self.default_questions = ["Когда впервые появилась проблема?", "При каких условиях проявляется сильнее?"]

    def get_questions(self, user_keywords: List[str]) -> List[str]:
        if not user_keywords:
            return self.default_questions[:2]
        best_score = 0
        best_questions = self.default_questions[:2]
        for theme in self.themes:
            score = 0
            for kw in user_keywords:
                if any(k in kw for k in theme.get("keywords", [])):
                    score += 1
            if score > best_score:
                best_score = score
                best_questions = theme.get("questions", self.default_questions)[:2]
        return best_questions

clarification_loader = ClarificationLoader()