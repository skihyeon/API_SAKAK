from pydantic import BaseModel, Field
from typing import Optional


class FoodNutritionBase(BaseModel):
    food_cd: str = Field(None, example="01")
    food_name: str = Field(None, example="test_food_name1")
    maker_name: Optional[str] = Field(None, example="test_maker_name1")
    
    
class FoodNutrition(FoodNutritionBase):
    id: int = Field(None, example=1)