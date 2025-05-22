from elasticsearch import Elasticsearch, ConnectionError
from typing import Optional, List, Dict, Any
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

_es_client: Optional[Elasticsearch] = None

def get_es_client() -> Elasticsearch:
    global _es_client
    if _es_client is None:
        try:
            logger.info(f"Elasticsearch 클라이언트 초기화 시도 (v7.x): {settings.ELASTICSEARCH_HOSTS}")
            client_options: Dict[str, Any] = {
                "hosts": settings.ELASTICSEARCH_HOSTS,
                "timeout": 30,
            }
            
            _es_client = Elasticsearch(**client_options)

            if not _es_client.ping():
                raise ConnectionError("Elasticsearch 서버에 연결할 수 없습니다 (ping 실패).")
            logger.info("Elasticsearch 클라이언트가 성공적으로 연결되었습니다 (v7.x).")
        except ConnectionError as e:
            logger.error(f"Elasticsearch 연결 실패 (v7.x): {e}")
            raise e
        except Exception as e:
            logger.error(f"Elasticsearch 클라이언트 생성 중 알 수 없는 오류 (v7.x): {e}")
            raise e
            
    return _es_client

def ping_es(es_client: Optional[Elasticsearch] = None) -> bool:
    """Elasticsearch 서버의 상태를 확인 (ping)합니다."""
    client_to_use = es_client if es_client is not None else get_es_client()
    try:
        return client_to_use.ping()
    except ConnectionError:
        logger.warning("ping_es: Elasticsearch 서버에 연결할 수 없습니다.")
        return False
    except Exception as e:
        logger.error(f"ping_es 중 오류 발생: {e}")
        return False
