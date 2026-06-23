from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class CarInfo(BaseModel):
    brand: str
    model: str
    year: int
    engine: Optional[str] = None
    generation: Optional[str] = None

class QueryRequest(BaseModel):
    message: str
    session_id: int
    car_info: Optional[CarInfo] = None
    context: Optional[str] = None
    pdf_path: Optional[str] = None
    history: Optional[List[Dict[str, str]]] = None

class QueryResponse(BaseModel):
    answer: str
    sources: List[Dict]
    suggested_pages: List[Dict]
    clarification_questions: List[str]
    session_id: int

class PageImageRequest(BaseModel):
    pdf_path: str
    page_number: int

class PageImageResponse(BaseModel):
    image_url: str
    page_number: int
    pdf_path: str