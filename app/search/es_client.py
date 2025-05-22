from elasticsearch import Elasticsearch, ConnectionError, helpers 
from typing import Optional, List, Dict, Any
import logging

from app.core.config import settings
from .es_utils import FOOD_NUTRITIONS_INDEX_NAME

logger = logging.getLogger(__name__)

_es_client: Optional[Elasticsearch] = None

def get_es_client() -> Elasticsearch:
    global _es_client
    if _es_client is None:
        try:
            logger.info(f"Elasticsearch 클라이언트 초기화 시도: {settings.ELASTICSEARCH_HOSTS}")
            client_options: Dict[str, Any] = {
                "hosts": settings.ELASTICSEARCH_HOSTS,
                "timeout": 30,
            }
            _es_client = Elasticsearch(**client_options)
            if not _es_client.ping():
                raise ConnectionError("Elasticsearch 서버에 연결할 수 없습니다.")
            logger.info("Elasticsearch 클라이언트가 성공적으로 연결되었습니다.")
        except ConnectionError as e:
            logger.error(f"Elasticsearch 연결 실패: {e}")
            raise e
        except Exception as e:
            logger.error(f"Elasticsearch 클라이언트 생성 중 알 수 없는 오류: {e}")
            raise e
    return _es_client


def ping_es(es_client: Optional[Elasticsearch] = None) -> bool:
    client_to_use = es_client if es_client is not None else get_es_client()
    try:
        return client_to_use.ping()
    except ConnectionError:
        logger.warning("ping_es: Elasticsearch 서버에 연결할 수 없습니다.")
        return False
    except Exception as e:
        logger.error(f"ping_es 중 오류 발생: {e}")
        return False

def search_food_nutritions_in_es(
    es_client: Elasticsearch,
    food_name: Optional[str] = None,
    research_year: Optional[str] = None,
    maker_name: Optional[str] = None,
    food_cd: Optional[str] = None,
    skip: int = 0,
    limit: int = 10
) -> List[Dict[str, Any]]:
    if not es_client:
        logger.warning("Elasticsearch 클라이언트가 제공되지 않아 검색을 수행할 수 없습니다.")
        return []

    query_conditions = []

    if food_name:
        query_conditions.append({"match": {"food_name": food_name}})
    
    if research_year:
        query_conditions.append({"term": {"research_year": research_year}})
        
    if maker_name:
        query_conditions.append({"match": {"maker_name": maker_name}})
  
    if food_cd:
        query_conditions.append({"term": {"food_cd": food_cd}})

    if not query_conditions:
        query_body = {"query": {"match_all": {}}, "from": skip, "size": limit}
    else:
        query_body = {
            "query": {
                "bool": {
                    "must": query_conditions
                }
            },
            "from": skip,
            "size": limit 
        }
    
    logger.info(f"Elasticsearch 검색 쿼리: {query_body}")
    
    try:
        response = es_client.search(
            index=FOOD_NUTRITIONS_INDEX_NAME,
            body=query_body
        )
        results = [hit["_source"] for hit in response["hits"]["hits"]]
        return results
    except es_exceptions.NotFoundError:
        logger.info(f"인덱스 '{FOOD_NUTRITIONS_INDEX_NAME}'를 찾을 수 없습니다.")
        return []
    except es_exceptions.ConnectionError as e:
        logger.error(f"Elasticsearch 검색 중 연결 오류 발생: {e}")
        return []
    except Exception as e:
        logger.error(f"Elasticsearch 검색 중 알 수 없는 오류 발생: {e}")
        return []