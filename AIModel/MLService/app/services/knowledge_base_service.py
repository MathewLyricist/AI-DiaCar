from sqlalchemy.orm import Session
from app.models.knowledge_base import KnowledgeEntry
import json


class KnowledgeBaseService:

    def __init__(self, db: Session):
        self.db = db

    def find_answer(self, topic: str, car_brand: str = None, car_model: str = None) -> dict:

        if car_brand and car_model:
            entry = self.db.query(KnowledgeEntry).filter(
                KnowledgeEntry.topic == topic,
                KnowledgeEntry.car_brand == car_brand,
                KnowledgeEntry.car_model == car_model
            ).order_by(KnowledgeEntry.priority.desc()).first()

            if entry:
                return self._parse_entry(entry)

        if car_brand:
            entry = self.db.query(KnowledgeEntry).filter(
                KnowledgeEntry.topic == topic,
                KnowledgeEntry.car_brand == car_brand,
                KnowledgeEntry.car_model == None
            ).order_by(KnowledgeEntry.priority.desc()).first()

            if entry:
                return self._parse_entry(entry)

        entry = self.db.query(KnowledgeEntry).filter(
            KnowledgeEntry.topic == topic,
            KnowledgeEntry.car_brand == None,
            KnowledgeEntry.car_model == None
        ).order_by(KnowledgeEntry.priority.desc()).first()

        if entry:
            return self._parse_entry(entry)

        return None

    def _parse_entry(self, entry: KnowledgeEntry) -> dict:
        return {
            'topic': entry.topic,
            'causes': json.loads(entry.causes) if entry.causes else [],
            'steps': json.loads(entry.steps) if entry.steps else [],
            'parameters': json.loads(entry.parameters) if entry.parameters else [],
            'manual_pages': entry.manual_pages,
        }