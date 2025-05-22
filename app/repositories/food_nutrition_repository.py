from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.food_nutrition import FoodNutrition as FoodNutritionModel

from app.schemas.food_nutrition import FoodNutritionCreate, FoodNutritionUpdate


def create_food_nutrition(db: Session, food_nutrition: FoodNutritionCreate) -> FoodNutritionModel:
    """
    새로운 음식 영양 정보를 데이터베이스에 생성합니다.
    Pydantic 스키마(FoodNutritionCreate)를 입력받아 SQLAlchemy 모델(FoodNutritionModel) 객체를 반환합니다.
    """
    db_food_nutrition = FoodNutritionModel(**food_nutrition.model_dump())
    db.add(db_food_nutrition)
    db.commit()
    db.refresh(db_food_nutrition)
    return db_food_nutrition

def get_food_nutrition(db: Session, food_nutrition_id: int) -> Optional[FoodNutritionModel]:
    """
    주어진 ID에 해당하는 음식 영양 정보를 데이터베이스에서 조회합니다.
    """
    return db.query(FoodNutritionModel).filter(FoodNutritionModel.id == food_nutrition_id).first()

def get_food_nutrition_by_food_cd(db: Session, food_cd: str) -> Optional[FoodNutritionModel]:
    """
    주어진 식품 코드(food_cd)에 해당하는 음식 영양 정보를 데이터베이스에서 조회합니다.
    """
    return db.query(FoodNutritionModel).filter(FoodNutritionModel.food_cd == food_cd).first()

def get_food_nutritions(
    db: Session, skip: int = 0, limit: int = 100
) -> List[FoodNutritionModel]:
    """
    음식 영양 정보 목록을 데이터베이스에서 조회합니다 (페이지네이션 적용).
    """
    return db.query(FoodNutritionModel).offset(skip).limit(limit).all()

def update_food_nutrition(
    db: Session, food_nutrition_id: int, food_nutrition_update: FoodNutritionUpdate
) -> Optional[FoodNutritionModel]:
    """
    주어진 ID에 해당하는 음식 영양 정보를 수정합니다.
    Pydantic 스키마(FoodNutritionUpdate)를 입력받아 업데이트합니다.
    """
    db_food_nutrition = db.query(FoodNutritionModel).filter(FoodNutritionModel.id == food_nutrition_id).first()
    if db_food_nutrition:
        update_data = food_nutrition_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_food_nutrition, key, value)
        db.add(db_food_nutrition)
        db.commit()
        db.refresh(db_food_nutrition)
    return db_food_nutrition

def delete_food_nutrition(db: Session, food_nutrition_id: int) -> Optional[FoodNutritionModel]:
    """
    주어진 ID에 해당하는 음식 영양 정보를 데이터베이스에서 삭제합니다.
    삭제된 객체 또는 None을 반환합니다.
    """
    db_food_nutrition = db.query(FoodNutritionModel).filter(FoodNutritionModel.id == food_nutrition_id).first()
    if db_food_nutrition:
        db.delete(db_food_nutrition)
        db.commit()
    return db_food_nutrition
