from pydantic_settings import BaseSettings
from pydantic.config import ConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "Food Nutrition API"
    APP_VERSION: str = "0.0.1"
    APP_DESCRIPTION: str = "API for food nutrition data"
    
    DATABASE_URL: str = "sqlite:///./food_nutrition_api.db"
    ELASTICSEARCH_URL: str = "http://localhost:9200"

settings = Settings()
    
    
    