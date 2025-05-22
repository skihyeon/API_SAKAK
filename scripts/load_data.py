import pandas as pd
from sqlalchemy.orm import Session
from elasticsearch import Elasticsearch, exceptions as es_exceptions
from elasticsearch.helpers import bulk
import logging
import math
import os

from app.db.session import SessionLocal
from app.models.food_nutrition import FoodNutrition as FoodNutritionModel
from app.schemas.food_nutrition import FoodNutritionCreate
from app.repositories import food_nutrition_repository
from app.search import get_es_client, FOOD_NUTRITIONS_INDEX_NAME

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

EXCEL_FILE_PATH = "data/food_data.xlsx" 

def safe_float_conversion(value, column_name_for_log="", food_cd_for_log=""):
    if pd.isna(value) or str(value).strip() == '-' or str(value).strip() == '':
        return None
    
    # "1g 미만"을 -1.0으로 치환
    if value == '1g 미만':
        logger.info(f"FoodCD '{food_cd_for_log}': 컬럼 '{column_name_for_log}'의 값 '{value}'을(를) -1.0으로 변환합니다 (1g 미만 의미).")
        return -1.0 

    try:
        return float(value)
    except ValueError:
        logger.warning(f"FoodCD '{food_cd_for_log}': 컬럼 '{column_name_for_log}'의 값 '{value}'을(를) float으로 변환할 수 없습니다. None으로 처리합니다.")
        return None

def safe_str_conversion(value):
    if pd.isna(value) or value is None:
        return None
    return str(value).strip()

def _get_es_doc_from_sqlalchemy_model(food_model: FoodNutritionModel) -> dict:
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

    logger.info("SQLite에서 기존 식품코드 조회 시작 (최적화 적용)...")
    all_excel_food_cds = set(df['식품코드'].astype(str).unique())
    existing_db_items_dict = {}
    
    excel_food_cds_list = list(all_excel_food_cds)
    chunk_size_for_select = 500 
    for i in range(0, len(excel_food_cds_list), chunk_size_for_select):
        food_cd_chunk = excel_food_cds_list[i:i + chunk_size_for_select]
        if food_cd_chunk:
            logger.info(f"SQLite에서 식품코드 {len(food_cd_chunk)}건에 대해 기존 데이터 조회 중 (청크 {i//chunk_size_for_select + 1})...")
            query_result = db.query(FoodNutritionModel).filter(FoodNutritionModel.food_cd.in_(food_cd_chunk)).all()
            for item in query_result:
                existing_db_items_dict[item.food_cd] = item
    logger.info(f"SQLite에서 총 {len(existing_db_items_dict)}개의 기존 식품 정보를 메모리에 로드했습니다.")

    es_actions = []
    newly_added_to_sqlite_count = 0
    already_in_sqlite_count = 0
    error_in_row_processing_count = 0

    logger.info("Excel 데이터 처리 및 SQLite 저장, Elasticsearch 인덱싱 준비 시작...")
    records = df.to_dict(orient='records')

    for row_dict in records:
        current_food_cd_for_log = str(row_dict.get('식품코드', '알수없음'))
        try:
            group_name_parts = []
            main_group = safe_str_conversion(row_dict.get('식품대분류'))
            sub_group = safe_str_conversion(row_dict.get('식품상세분류'))
            if main_group: group_name_parts.append(main_group)
            if sub_group: group_name_parts.append(sub_group)
            combined_group_name = " - ".join(group_name_parts) if group_name_parts else None

            ref_name_val = safe_str_conversion(row_dict.get('성분표출처'))

            food_data_to_create = FoodNutritionCreate(
                food_cd=str(row_dict['식품코드']),
                food_name=str(row_dict['식품명']),
                group_name=combined_group_name,
                research_year=safe_str_conversion(row_dict.get('연도')),
                maker_name=safe_str_conversion(row_dict.get('지역 / 제조사')),
                ref_name=ref_name_val,
                serving_size=safe_float_conversion(row_dict.get('1회제공량'), '1회제공량', current_food_cd_for_log),
                calorie=safe_float_conversion(row_dict.get('에너지(㎉)'), '에너지(㎉)', current_food_cd_for_log),
                carbohydrate=safe_float_conversion(row_dict.get('탄수화물(g)'), '탄수화물(g)', current_food_cd_for_log),
                protein=safe_float_conversion(row_dict.get('단백질(g)'), '단백질(g)', current_food_cd_for_log),
                province=safe_float_conversion(row_dict.get('지방(g)'), '지방(g)', current_food_cd_for_log),
                sugars=safe_float_conversion(row_dict.get('총당류(g)'), '총당류(g)', current_food_cd_for_log),
                salt=safe_float_conversion(row_dict.get('나트륨(㎎)'), '나트륨(㎎)', current_food_cd_for_log),
                cholesterol=safe_float_conversion(row_dict.get('콜레스테롤(㎎)'), '콜레스테롤(㎎)', current_food_cd_for_log),
                saturated_fatty_acids=safe_float_conversion(row_dict.get('총 포화 지방산(g)'), '총 포화 지방산(g)', current_food_cd_for_log),
                trans_fat=safe_float_conversion(row_dict.get('트랜스 지방산(g)'), '트랜스 지방산(g)', current_food_cd_for_log),
            )

            db_item_for_es = existing_db_items_dict.get(food_data_to_create.food_cd)
            
            if db_item_for_es:
                already_in_sqlite_count += 1
            else:
                db_item_for_es = food_nutrition_repository.create_food_nutrition(
                    db=db, 
                    food_nutrition=food_data_to_create, 
                    sync_to_es=False 
                )
                if db_item_for_es:
                    newly_added_to_sqlite_count += 1
                    existing_db_items_dict[db_item_for_es.food_cd] = db_item_for_es
                else:
                    logger.error(f"FoodCD '{current_food_cd_for_log}': SQLite 저장에 실패했습니다 (Repository에서 None 반환).")
                    error_in_row_processing_count +=1
                    continue 
            
            if es_client and db_item_for_es:
                es_document_cleaned = _get_es_doc_from_sqlalchemy_model(db_item_for_es)
                action = {
                    "_index": FOOD_NUTRITIONS_INDEX_NAME,
                    "_id": str(db_item_for_es.id),
                    "_source": es_document_cleaned
                }
                es_actions.append(action)

        except KeyError as e:
            logger.error(f"Excel 파일의 레코드 처리 중 누락된 필수 컬럼 오류: {e}. FoodCD: {current_food_cd_for_log}. 해당 레코드 건너뜀.")
            error_in_row_processing_count +=1
            continue
        except Exception as e:
            logger.error(f"Excel 파일의 레코드 처리 중 일반 오류 발생: {e}. FoodCD: {current_food_cd_for_log}, RowData: {row_dict}. 해당 레코드 건너뜀.")
            error_in_row_processing_count +=1
            continue

    logger.info(f"Excel 데이터 반복 처리 완료. SQLite에 새로 추가: {newly_added_to_sqlite_count}건, 이미 존재(메모리 확인): {already_in_sqlite_count}건, 처리 중 오류: {error_in_row_processing_count}건.")

    if es_client and es_actions:
        logger.info(f"Elasticsearch에 {len(es_actions)}건의 문서 bulk 인덱싱 시작...")
        try:
            successes, errors = bulk(
                client=es_client,
                actions=es_actions,
                raise_on_error=False, 
                refresh=False,    
                chunk_size=1000,     
                request_timeout=60   
            )
            logger.info(f"Elasticsearch bulk 인덱싱 완료: 성공 {successes}건, 실패 {len(errors)}건.")
            if errors:
                logger.error(f"Elasticsearch bulk 인덱싱 실패 상세 (최대 5건): {errors[:5]}")
        except Exception as e:
            logger.error(f"Elasticsearch bulk 인덱싱 중 치명적 오류 발생: {e}")
    elif es_client:
        logger.info("Elasticsearch로 인덱싱할 작업이 없습니다 (es_actions 비어있음).")
    
    db.close()
    logger.info("데이터 로딩 스크립트 실행 완료.")


if __name__ == "__main__":
    logger.info("데이터 로딩 프로세스를 시작합니다...")
    load_excel_to_db_and_es()