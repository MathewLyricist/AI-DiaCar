import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))

    MANUALS_PATH = "/home/mathew/Политех/4-й курс/ВКР/ Project/AI DiaCar/AI-DiaCar/AIModel/DataPDF"
    VECTORSTORE_PATH: str = os.getenv("VECTORSTORE_PATH", "./data/vectorstore")

    EMBEDDING_MODEL: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "300"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "30"))

    TOP_K_RESULTS: int = int(os.getenv("TOP_K_RESULTS", "5"))
    SCORE_THRESHOLD: float = float(os.getenv("SCORE_THRESHOLD", "0.5"))

    BACKEND_URL: str = os.getenv("BACKEND_URL", "http://localhost:8080")

    IMAGES_PATH: str = os.getenv("IMAGES_PATH", "./data/images")
    IMAGE_DPI: int = int(os.getenv("IMAGE_DPI", "200"))

    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./aidiacar.db")

    AUTO_INDEX_IF_EMPTY: bool = True
    FORCE_REINDEX_ON_START: bool = False

    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_MODEL: str = os.getenv("OPENROUTER_MODEL", "google/gemma-2-9b-it:free")

    USE_VECTOR_STORE: bool = False

    JSON_KNOWLEDGE_PATH: str = "/home/mathew/Политех/4-й курс/ВКР/ Project/AI DiaCar/AI-DiaCar/AIModel/DataPDF"
    CLARIFICATION_QUESTIONS_PATH: str = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "clarification_questions.json")

    JSON_VECTORSTORE_PATH: str = os.getenv("JSON_VECTORSTORE_PATH", "./data/json_vectorstore")
    JSON_SEARCH_TOP_K: int = int(os.getenv("JSON_SEARCH_TOP_K", "3"))
    JSON_SIMILARITY_THRESHOLD: float = float(os.getenv("JSON_SIMILARITY_THRESHOLD", "0.7"))

    JSON_SIMILARITY_THRESHOLD_FALLBACK: float = float(os.getenv("JSON_SIMILARITY_THRESHOLD_FALLBACK", "0.6"))

    LLM_ENABLED: bool = os.getenv("LLM_ENABLED", "True").lower() == "true"
    LLM_MODEL_NAME: str = os.getenv("LLM_MODEL_NAME", "google/flan-t5-small")
    LLM_DEVICE: str = os.getenv("LLM_DEVICE", "cpu")
    LLM_MAX_NEW_TOKENS: int = int(os.getenv("LLM_MAX_NEW_TOKENS", "256"))
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.2"))
    HIGH_THRESHOLD = 7.5
    LOW_THRESHOLD = 6.0

settings = Settings()

print(f"JSON_KNOWLEDGE_PATH: {settings.JSON_KNOWLEDGE_PATH} -> exists: {os.path.exists(settings.JSON_KNOWLEDGE_PATH)}")
print(f"CLARIFICATION_QUESTIONS_PATH: {settings.CLARIFICATION_QUESTIONS_PATH} -> exists: {os.path.exists(settings.CLARIFICATION_QUESTIONS_PATH)}")