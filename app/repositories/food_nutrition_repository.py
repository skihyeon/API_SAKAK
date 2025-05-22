from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import logging

from app.models.food_nutrition import FoodNutrition as FoodNutritionModel
from app.schemas.food_nutrition import FoodNutritionCreate, FoodNutritionUpdate

from elasticsearch import Elasticsearch, exceptions as es_exceptions
from app.search import get_es_client, FOOD_NUTRITIONS_INDEX_NAME

logger = logging.getLogger(__name__)

def _get_es_doc_from_model(food_model: FoodNutritionModel) -> Dict[str, Any]:
    doc = {
        "id": food_model.id,
        "food_cd": food_model.food_cd,
        "group_name": food_model.group_name,
        "food_name": food_model.food_name,
        "research_year": food_model.research_year,
        "maker_name": food_model.maker_name,
        "ref_name": food_model.ref_name,
        "serving_size": food_model.serving_size,
        "calorie": food_model.calorie,
        "carbohydrate": food_model.carbohydrate,
        "protein": food_model.protein,
        "province": food_model.province,
        "sugars": food_model.sugars,
        "salt": food_model.salt,
        "cholesterol": food_model.cholesterol,
        "saturated_fatty_acids": food_model.saturated_fatty_acids,
        "trans_fat": food_model.trans_fat,
    }
    return {k: v for k, v in doc.items() if v is not None}


def create_food_nutrition(
    db: Session, 
    food_nutrition: FoodNutritionCreate, 
    sync_to_es: bool = True
) -> FoodNutritionModel:
    db_food_nutrition = FoodNutritionModel(**food_nutrition.model_dump())
    db.add(db_food_nutrition)
    db.commit()
    db.refresh(db_food_nutrition)
    logger.info(f"SQLite: FoodNutrition ID {db_food_nutrition.id} ({db_food_nutrition.food_name}) 생성 완료.")

    if sync_to_es:
        try:
            es_client = get_es_client()
            if es_client.ping():
                doc_body = _get_es_doc_from_model(db_food_nutrition)
                es_client.index(
                    index=FOOD_NUTRITIONS_INDEX_NAME,
                    id=str(db_food_nutrition.id),
                    body=doc_body,
                    refresh="wait_for"
                )
                logger.info(f"Elasticsearch: FoodNutrition ID {db_food_nutrition.id} 인덱싱 완료 (즉시 동기화).")
            else:
                logger.warning(f"ES Connection Error: FoodNutrition ID {db_food_nutrition.id} 즉시 동기화 실패 (ping 실패).")
        except es_exceptions.ConnectionError as e:
            logger.error(f"ES Connection Error: FoodNutrition ID {db_food_nutrition.id} 즉시 동기화 중 연결 오류: {e}")
        except Exception as e:
            logger.error(f"ES Error: FoodNutrition ID {db_food_nutrition.id} 즉시 동기화 중 오류: {e}")
            
    return db_food_nutrition


def update_food_nutrition(
    db: Session, 
    food_nutrition_id: int, 
    food_nutrition_update: FoodNutritionUpdate,
    sync_to_es: bool = True
) -> Optional[FoodNutritionModel]:
    db_food_nutrition = db.query(FoodNutritionModel).filter(FoodNutritionModel.id == food_nutrition_id).first()
    if db_food_nutrition:
        update_data = food_nutrition_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_food_nutrition, key, value)
        db.add(db_food_nutrition)
        db.commit()
        db.refresh(db_food_nutrition)
        logger.info(f"SQLite: FoodNutrition ID {db_food_nutrition.id} 업데이트 완료.")

        if sync_to_es:
            try:
                es_client = get_es_client()
                if es_client.ping():
                    doc_body = _get_es_doc_from_model(db_food_nutrition)
                    es_client.index(
                        index=FOOD_NUTRITIONS_INDEX_NAME,
                        id=str(db_food_nutrition.id),
                        body=doc_body,
                        refresh="wait_for"
                    )
                    logger.info(f"Elasticsearch: FoodNutrition ID {db_food_nutrition.id} 업데이트 완료 (즉시 동기화).")
                else:
                    logger.warning(f"ES Connection Error: FoodNutrition ID {db_food_nutrition.id} 즉시 동기화 업데이트 실패 (ping 실패).")
            except es_exceptions.ConnectionError as e:
                logger.error(f"ES Connection Error: FoodNutrition ID {db_food_nutrition.id} 즉시 동기화 업데이트 중 연결 오류: {e}")
            except Exception as e:
                logger.error(f"ES Error: FoodNutrition ID {db_food_nutrition.id} 즉시 동기화 업데이트 중 오류: {e}")
            
        return db_food_nutrition
    return None


def delete_food_nutrition(
    db: Session, 
    food_nutrition_id: int,
    sync_to_es: bool = True
) -> Optional[FoodNutritionModel]:
    db_food_nutrition = db.query(FoodNutritionModel).filter(FoodNutritionModel.id == food_nutrition_id).first()
    if db_food_nutrition:
        deleted_item_id_str = str(db_food_nutrition.id)
        db.delete(db_food_nutrition)
        db.commit()
        logger.info(f"SQLite: FoodNutrition ID {deleted_item_id_str} 삭제 완료.")

        if sync_to_es:
            try:
                es_client = get_es_client()
                if es_client.ping():
                    es_client.delete(
                        index=FOOD_NUTRITIONS_INDEX_NAME,
                        id=deleted_item_id_str,
                        refresh="wait_for"
                    )
                    logger.info(f"Elasticsearch: FoodNutrition ID {deleted_item_id_str} 삭제 완료 (즉시 동기화).")
                else:
                    logger.warning(f"ES Connection Error: FoodNutrition ID {deleted_item_id_str} 즉시 동기화 삭제 실패 (ping 실패).")
            except es_exceptions.NotFoundError:
                logger.warning(f"ES Warning: FoodNutrition ID {deleted_item_id_str} (은)는 Elasticsearch 인덱스에 존재하지 않아 삭제할 수 없습니다.")
            except es_exceptions.ConnectionError as e:
                logger.error(f"ES Connection Error: FoodNutrition ID {deleted_item_id_str} 즉시 동기화 삭제 중 연결 오류: {e}")
            except Exception as e:
                logger.error(f"ES Error: FoodNutrition ID {deleted_item_id_str} 즉시 동기화 삭제 중 오류: {e}")

        return db_food_nutrition
    logger.warning(f"SQLite: 삭제할 FoodNutrition ID {food_nutrition_id} (을)를 찾지 못했습니다.")
    return None

def get_food_nutrition(db: Session, food_nutrition_id: int) -> Optional[FoodNutritionModel]:
    return db.query(FoodNutritionModel).filter(FoodNutritionModel.id == food_nutrition_id).first()

def get_food_nutrition_by_food_cd(db: Session, food_cd: str) -> Optional[FoodNutritionModel]:
    return db.query(FoodNutritionModel).filter(FoodNutritionModel.food_cd == food_cd).first()

def get_food_nutritions(
    db: Session, skip: int = 0, limit: int = 100
) -> List[FoodNutritionModel]:
    return db.query(FoodNutritionModel).offset(skip).limit(limit).all()