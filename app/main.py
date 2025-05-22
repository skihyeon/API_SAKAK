from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.api.v1.endpoints import food_nutritions as food_nutritions_router
from app.search import (
    get_es_client,
    ping_es,
    create_index_if_not_exists,
    FOOD_NUTRITIONS_INDEX_NAME,
    FOOD_NUTRITIONS_MAPPINGS
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("FastAPI 애플리케이션 시작 중...")
    try:
        es_client = get_es_client()
        create_index_if_not_exists(
            es_client=es_client,
            index_name=FOOD_NUTRITIONS_INDEX_NAME,
            mappings_body=FOOD_NUTRITIONS_MAPPINGS
        )
    except Exception as e:
        logger.error(f"애플리케이션 시작 중 Elasticsearch 관련 설정 오류 발생: {e}")
    
    yield
    
    logger.info("FastAPI 애플리케이션 종료 중...")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
    lifespan=lifespan
)

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": f"Welcome to {settings.APP_NAME}! API version: {settings.APP_VERSION}"}

@app.get("/health", tags=["Health Check"])
async def health_check():
    es_ping_ok = False
    try:
        es_ping_ok = ping_es() 
    except Exception:
        pass
    es_status = "connected" if es_ping_ok else "disconnected"
    
    return {
        "status": "ok",
        "message": f"{settings.APP_NAME} is healthy.",
        "elasticsearch_status": es_status
    }

app.include_router(
    food_nutritions_router.router,
    prefix="/api/v1/food-nutritions",
    tags=["FoodNutritions API"]
)