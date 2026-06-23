from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class KnowledgeEntry(Base):
    __tablename__ = "knowledge_entries"

    id = Column(Integer, primary_key=True)
    topic = Column(String(100), nullable=False)
    car_brand = Column(String(50))
    car_model = Column(String(50))
    question_pattern = Column(Text)
    causes = Column(Text)
    steps = Column(Text)
    parameters = Column(Text)
    manual_pages = Column(String(100))
    priority = Column(Integer, default=0)


class PDFManual(Base):
    __tablename__ = "pdf_manuals"

    id = Column(Integer, primary_key=True)
    car_brand = Column(String(50))
    car_model = Column(String(50))
    file_path = Column(String(500))
    extracted_text = Column(Text)
    processed_at = Column(String(50))