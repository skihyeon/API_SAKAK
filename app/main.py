from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.endpoints import foods as foods_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
)

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": f"Welcome to {settings.APP_NAME}! API version: {settings.APP_VERSION}"}

@app.get("/health", tags=["Health Check"])
async def health_check():
    return {"status": "ok", "message": f"{settings.APP_NAME} is healthy."}

app.include_router(foods_router.router, prefix="/api/v1/foods", tags=["Foods API (Mocked)"])
