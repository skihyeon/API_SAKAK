from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Food Nutrition API"
    APP_VERSION: str = "0.0.1"
    APP_DESCRIPTION: str = "API for food nutrition data"
    
    class Config:
        pass

settings = Settings()
    
    
    