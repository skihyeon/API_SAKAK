import logging
logging.basicConfig(level=logging.INFO)

from app.search import get_es_client, ping_es
from app.core.config import settings

print(f"설정된 Elasticsearch 호스트: {settings.ELASTICSEARCH_HOSTS}")
try:
    es = get_es_client()
    if es.ping():
        print("SUCCESS: Elasticsearch 서버에 성공적으로 연결되었습니다.")
    else:
        print("ERROR: Elasticsearch 서버에 연결되었으나 ping에 실패했습니다.")
except Exception as e:
    print(f"ERROR: Elasticsearch 연결 중 오류 발생: {e}")