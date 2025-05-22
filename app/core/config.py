from pydantic_settings import BaseSettings
from pydantic.config import ConfigDict
from typing import List
import os

class Settings(BaseSettings):
    APP_NAME: str = "Food Nutrition API"
    APP_VERSION: str = "0.0.1"
    APP_DESCRIPTION: str = "API for food nutrition data"
    
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./food_nutrition_api.db")
    ES_HOST: str = os.getenv("ES_HOST", "http://localhost:9200")
    
    @property
    def ELASTICSEARCH_HOSTS(self) -> List[str]:
        return [self.ES_HOST]

settings = Settings()
    
    
    