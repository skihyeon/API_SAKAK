from elasticsearch import Elasticsearch, exceptions as es_exceptions
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

FOOD_NUTRITIONS_INDEX_NAME = "food_nutritions_idx"

FOOD_NUTRITIONS_MAPPINGS = {
    "mappings": {
        "properties": {
            "id": {"type": "integer"},
            "food_cd": {"type": "keyword"},
            "group_name": {"type": "text", "fields": {"keyword": {"type": "keyword", "ignore_above": 256}}},
            "food_name": {"type": "text", "analyzer": "standard", "fields": {"keyword": {"type": "keyword", "ignore_above": 256}}},
            "research_year": {"type": "keyword"},
            "maker_name": {"type": "text", "fields": {"keyword": {"type": "keyword", "ignore_above": 256}}},
            "ref_name": {"type": "text", "fields": {"keyword": {"type": "keyword", "ignore_above": 256}}},
            "serving_size": {"type": "float"},
            "calorie": {"type": "float"},
            "carbohydrate": {"type": "float"},
            "protein": {"type": "float"},
            "province": {"type": "float"},
            "sugars": {"type": "float"},
            "salt": {"type": "float"},
            "cholesterol": {"type": "float"},
            "saturated_fatty_acids": {"type": "float"},
            "trans_fat": {"type": "float"}
        }
    }
}

def create_index_if_not_exists(es_client: Elasticsearch, index_name: str, mappings_body: Dict[str, Any]):
    try:
        if not es_client.indices.exists(index=index_name):
            es_client.indices.create(index=index_name, body=mappings_body)
            logger.info(f"Elasticsearch 인덱스 '{index_name}' (이)가 성공적으로 생성되었습니다.")
        else:
            logger.info(f"Elasticsearch 인덱스 '{index_name}' (은)는 이미 존재합니다.")
    except es_exceptions.ConnectionError as e:
        logger.error(f"Elasticsearch 연결 오류로 인덱스 '{index_name}' 확인/생성 실패: {e}")
    except Exception as e:
        logger.error(f"Elasticsearch 인덱스 '{index_name}' 생성 중 알 수 없는 오류 발생: {e}")