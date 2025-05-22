import pandas as pd
from sqlalchemy.orm import Session
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import logging
import math

from app.db.session import SessionLocal
from app.models.food_nutrition import FoodNutrition as FoodNutritionModel
from app.schemas.food_nutrition import FoodNutritionCreate
from app.repositories import food_nutrition_repository
from app.search import get_es_client, FOOD_NUTRITIONS_INDEX_NAME, FOOD_NUTRITIONS_MAPPINGS 

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

EXCEL_FILE_PATH = "data/food_data.xlsx"

def safe_float_conversion(value, column_name_for_log="", food_cd_for_log=""):
    if pd.isna(value) or str(value).strip() == '-' or str(value).strip() == '':
        return None
    try:
        return float(value)
    except ValueError:
        logger.warning(f"FoodCD '{food_cd_for_log}': 컬럼 '{column_name_for_log}'의 값 '{value}'을(를) float으로 변환할 수 없습니다. None으로 처리합니다.")
        return None

def safe_str_conversion(value):
    if pd.isna(value) or value is None:
        return None
    return str(value).strip()


def load_excel_to_db_and_es():
    db: Session = SessionLocal()
    es_client: Elasticsearch = None

    try:
        es_client = get_es_client()
        if not es_client.ping():
            logger.warning("Elasticsearch 서버에 연결할 수 없습니다. 데이터는 SQLite에만 적재됩니다.")
            es_client = None
    except Exception as e:
        logger.warning(f"Elasticsearch 클라이언트 생성 중 오류: {e}. 데이터는 SQLite에만 적재됩니다.")
        es_client = None

    logger.info(f"'{EXCEL_FILE_PATH}'에서 데이터 로딩 시작...")
    try:
        df = pd.read_excel(EXCEL_FILE_PATH, na_values=['-'])
        logger.info(f"Excel 파일에서 {len(df)}개의 행을 읽었습니다.")
    except FileNotFoundError:
        logger.error(f"Excel 파일을 찾을 수 없습니다: {EXCEL_FILE_PATH}")
        db.close()
        return
    except Exception as e:
        logger.error(f"Excel 파일 읽기 중 오류 발생: {e}")
        db.close()
        return

    es_actions = []
    newly_added_to_sqlite_count = 0
    already_in_sqlite_count = 0
    error_in_row_processing_count = 0

    for index, row in df.iterrows():
        current_food_cd_for_log = str(row.get('식품코드', '알수없음'))
        try:
            group_name_parts = []
            main_group = safe_str_conversion(row.get('식품대분류'))
            sub_group = safe_str_conversion(row.get('식품상세분류'))
            if main_group:
                group_name_parts.append(main_group)
            if sub_group:
                group_name_parts.append(sub_group)
            combined_group_name = " - ".join(group_name_parts) if group_name_parts else None

            ref_name_val = safe_str_conversion(row.get('성분표출처'))

            food_data_create = FoodNutritionCreate(
                food_cd=str(row['식품코드']),
                food_name=str(row['식품명']),
                group_name=combined_group_name,
                research_year=safe_str_conversion(row.get('연도')),
                maker_name=safe_str_conversion(row.get('지역 / 제조사')),
                ref_name=ref_name_val,
                serving_size=safe_float_conversion(row.get('1회제공량'), '1회제공량', current_food_cd_for_log),
                calorie=safe_float_conversion(row.get('에너지(㎉)'), '에너지(㎉)', current_food_cd_for_log),
                carbohydrate=safe_float_conversion(row.get('탄수화물(g)'), '탄수화물(g)', current_food_cd_for_log),
                protein=safe_float_conversion(row.get('단백질(g)'), '단백질(g)', current_food_cd_for_log),
                province=safe_float_conversion(row.get('지방(g)'), '지방(g)', current_food_cd_for_log),
                sugars=safe_float_conversion(row.get('총당류(g)'), '총당류(g)', current_food_cd_for_log),
                salt=safe_float_conversion(row.get('나트륨(㎎)'), '나트륨(㎎)', current_food_cd_for_log),
                cholesterol=safe_float_conversion(row.get('콜레스테롤(㎎)'), '콜레스테롤(㎎)', current_food_cd_for_log),
                saturated_fatty_acids=safe_float_conversion(row.get('총 포화 지방산(g)'), '총 포화 지방산(g)', current_food_cd_for_log),
                trans_fat=safe_float_conversion(row.get('트랜스 지방산(g)'), '트랜스 지방산(g)', current_food_cd_for_log),
            )

            existing_item_in_db = food_nutrition_repository.get_food_nutrition_by_food_cd(db, food_cd=food_data_create.food_cd)
            db_item_for_es = None
            if existing_item_in_db:
                already_in_sqlite_count += 1
                db_item_for_es = existing_item_in_db
            else:
                db_item_for_es = food_nutrition_repository.create_food_nutrition(db=db, food_nutrition=food_data_create)
                newly_added_to_sqlite_count += 1
            
            if es_client and db_item_for_es:
                es_document = {
                    "id": db_item_for_es.id,
                    "food_cd": db_item_for_es.food_cd,
                    "group_name": db_item_for_es.group_name,
                    "food_name": db_item_for_es.food_name,
                    "research_year": db_item_for_es.research_year,
                    "maker_name": db_item_for_es.maker_name,
                    "ref_name": db_item_for_es.ref_name,
                    "serving_size": db_item_for_es.serving_size,
                    "calorie": db_item_for_es.calorie,
                    "carbohydrate": db_item_for_es.carbohydrate,
                    "protein": db_item_for_es.protein,
                    "province": db_item_for_es.province,
                    "sugars": db_item_for_es.sugars,
                    "salt": db_item_for_es.salt,
                    "cholesterol": db_item_for_es.cholesterol,
                    "saturated_fatty_acids": db_item_for_es.saturated_fatty_acids,
                    "trans_fat": db_item_for_es.trans_fat,
                }
                es_document_cleaned = {k: v for k, v in es_document.items() if v is not None}
                action = {"_index": FOOD_NUTRITIONS_INDEX_NAME, "_id": db_item_for_es.id, "_source": es_document_cleaned}
                es_actions.append(action)

        except KeyError as e:
            logger.error(f"Excel 파일의 {index + 2}번째 행 처리 중 누락된 필수 컬럼 오류: {e}. 해당 행 건너뜀. (FoodCD: {current_food_cd_for_log})")
            error_in_row_processing_count +=1
            continue
        except Exception as e:
            logger.error(f"Excel 파일의 {index + 2}번째 행 처리 중 일반 오류 발생: {e}. 해당 행 건너뜀. (FoodCD: {current_food_cd_for_log}, RowData: {row.to_dict()})")
            error_in_row_processing_count +=1
            continue

    logger.info(f"Excel 파일 처리 완료. SQLite에 새로 추가: {newly_added_to_sqlite_count}건, 이미 존재(SQLite): {already_in_sqlite_count}건, 처리 중 오류: {error_in_row_processing_count}건.")

    if es_client and es_actions:
        logger.info(f"Elasticsearch에 {len(es_actions)}건의 문서 bulk 인덱싱 시작...")
        try:
            successes, errors = bulk(client=es_client, actions=es_actions, raise_on_error=False, refresh=True)
            logger.info(f"Elasticsearch bulk 인덱싱 완료: 성공 {successes}건, 실패 {len(errors)}건.")
            if errors:
                logger.error(f"Elasticsearch bulk 인덱싱 실패 상세 (최대 5건): {errors[:5]}")
        except Exception as e:
            logger.error(f"Elasticsearch bulk 인덱싱 중 치명적 오류 발생: {e}")
    elif es_client:
        logger.info("Elasticsearch로 인덱싱할 작업이 없습니다.")
    
    db.close()
    logger.info("데이터 로딩 스크립트 실행 완료.")

if __name__ == "__main__":
    logger.info("데이터 로딩 프로세스를 시작합니다...")
    load_excel_to_db_and_es()