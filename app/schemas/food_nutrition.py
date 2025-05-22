from pydantic import BaseModel, Field
from typing import Optional, List 
from pydantic.config import ConfigDict

class FoodNutritionBase(BaseModel):
    food_cd: str = Field(..., json_schema_extra={'example': "01"}, description="식품코드드")
    food_name: str = Field(..., json_schema_extra={'example': "example_food_name"}, description="식품이름")
    group_name: Optional[str] = Field(None, json_schema_extra={'example': "example_group_name"}, description="식품군")
    research_year: Optional[str] = Field(None, json_schema_extra={'example': "2025"}, description="조사년도")
    maker_name: Optional[str] = Field(None, json_schema_extra={'example': "example_maker_name"}, description="지역/제조사")
    ref_name: Optional[str] = Field(None, json_schema_extra={'example': "example_ref_name"}, description="자료출처")
    serving_size: Optional[float] = Field(None, json_schema_extra={'example': 100.0}, description="1회 제공량")
    calorie: Optional[float] = Field(None, json_schema_extra={'example': 30.5}, description="열량(kcal)(1회제공량당)")
    carbohydrate: Optional[float] = Field(None, json_schema_extra={'example': 5.5}, description="탄수화물(g)(1회제공량당)")
    protein: Optional[float] = Field(None, json_schema_extra={'example': 2.1}, description="단백질(g)(1회제공량당)")
    province: Optional[float] = Field(None, json_schema_extra={'example': 0.5}, description="지방(g)(1회제공량당)")
    sugars: Optional[float] = Field(None, json_schema_extra={'example': 1.0}, description="총당류(g)(1회제공량당)")
    salt: Optional[float] = Field(None, json_schema_extra={'example': 700.0}, description="나트륨(mg)(1회제공량당)")
    cholesterol: Optional[float] = Field(None, json_schema_extra={'example': 0.0}, description="콜레스테롤(mg)(1회제공량당)")
    saturated_fatty_acids: Optional[float] = Field(None, json_schema_extra={'example': 0.1}, description="포화지방산(g)(1회제공량당)")
    trans_fat: Optional[float] = Field(None, json_schema_extra={'example': 0.0}, description="트랜스지방(g)(1회제공량당)")

## C: Create는 FoodNutritionBase schema를 상속받아서 생성.
class FoodNutritionCreate(FoodNutritionBase):
    pass 

## U: Update는 원하는 값만 수정할 수 있게 모든 필드를 Optional로 설정.
class FoodNutritionUpdate(BaseModel):
    food_cd: Optional[str] = Field(None, json_schema_extra={'example': "01"}, description="식품코드")
    food_name: Optional[str] = Field(None, json_schema_extra={'example': "example_food_name"}, description="식품이름")
    group_name: Optional[str] = Field(None, json_schema_extra={'example': "example_group_name"}, description="식품군")
    research_year: Optional[str] = Field(None, json_schema_extra={'example': "2025"}, description="조사년도")
    maker_name: Optional[str] = Field(None, json_schema_extra={'example': "example_maker_name"}, description="지역/제조사")
    ref_name: Optional[str] = Field(None, json_schema_extra={'example': "example_ref_name"}, description="자료출처")
    serving_size: Optional[float] = Field(None, json_schema_extra={'example': 100.0}, description="1회 제공량")
    calorie: Optional[float] = Field(None, json_schema_extra={'example': 30.5}, description="열량(kcal)(1회제공량당)")
    carbohydrate: Optional[float] = Field(None, json_schema_extra={'example': 5.5}, description="탄수화물(g)(1회제공량당)")
    protein: Optional[float] = Field(None, json_schema_extra={'example': 2.1}, description="단백질(g)(1회제공량당)")
    province: Optional[float] = Field(None, json_schema_extra={'example': 0.5}, description="지방(g)(1회제공량당)")
    sugars: Optional[float] = Field(None, json_schema_extra={'example': 1.0}, description="총당류(g)(1회제공량당)")
    salt: Optional[float] = Field(None, json_schema_extra={'example': 700.0}, description="나트륨(mg)(1회제공량당)")
    cholesterol: Optional[float] = Field(None, json_schema_extra={'example': 0.0}, description="콜레스테롤(mg)(1회제공량당)")
    saturated_fatty_acids: Optional[float] = Field(None, json_schema_extra={'example': 0.1}, description="포화지방산(g)(1회제공량당)")
    trans_fat: Optional[float] = Field(None, json_schema_extra={'example': 0.0}, description="트랜스지방(g)(1회제공량당)")



## DB에서 읽어온 데이터
class FoodNutritionInDBBase(FoodNutritionBase):
    id: int = Field(..., json_schema_extra={'example': 1}, description="Id")
    model_config = ConfigDict(from_attributes=True)

## R: API 응답용 스키마
class FoodNutrition(FoodNutritionInDBBase):
    pass

## Search API 응답용 스키마
class FoodNutritionSearchResponse(BaseModel):
    id: int
    food_cd: str
    group_name: Optional[str] = None
    food_name: str
    research_year: Optional[str] = None
    maker_name: Optional[str] = None
    ref_name: Optional[str] = None
    serving_size: Optional[float] = None
    calorie: Optional[float] = None
    carbohydrate: Optional[float] = None
    protein: Optional[float] = None
    province: Optional[float] = None
    sugars: Optional[float] = None
    salt: Optional[float] = None
    cholesterol: Optional[float] = None
    saturated_fatty_acids: Optional[float] = None
    trans_fat: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)