from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.routes import router
from app.config import settings
from app.database import init_db
import logging
import os

os.environ["CHROMA_MEMORY_LIMIT_BYTES"] = "8589934592"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

init_db()
logger.info("✅ База данных инициализирована")

app = FastAPI(
    title="AI DiaCar ML Service",
    description="ML сервис для анализа запросов на основе технической документации",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(settings.IMAGES_PATH, exist_ok=True)
app.mount("/images", StaticFiles(directory=settings.IMAGES_PATH), name="images")

from app.services.llm_service import LLMService

app.state.llm_service = LLMService()
if app.state.llm_service.enabled:
    logger.info(f"✅ LLM Service инициализирован (модель: {settings.LLM_MODEL_NAME})")
else:
    logger.warning("⚠️ LLM Service отключён или не загрузился, будет использован fallback")

app.include_router(router, prefix="/api/ml", tags=["ML"])

@app.get("/")
async def root():
    return {"message": "AI DiaCar ML Service is running", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )