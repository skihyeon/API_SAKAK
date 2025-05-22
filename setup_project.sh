#!/bin/bash

# 스크립트 실행 중 오류가 발생하면 즉시 중단합니다.
set -e

echo "======================================================"
echo " Food Nutrition API 프로젝트 설정 및 실행을 시작합니다. "
echo "======================================================"
echo "현재 작업 디렉토리: $(pwd)" # 현재 작업 디렉토리 명시

# Docker Compose 서비스 이름 정의
APP_SERVICE_NAME="app"
ES_SERVICE_NAME="es01"

# 사용 가능한 Docker Compose 명령어 자동 탐지 및 설정
COMPOSE_CMD=""
if docker compose version >/dev/null 2>&1; then
    echo "INFO: Docker Compose V2 ('docker compose')를 사용합니다."
    COMPOSE_CMD="docker compose"
elif docker-compose --version >/dev/null 2>&1; then
    echo "INFO: Docker Compose V1 ('docker-compose')를 사용합니다."
    COMPOSE_CMD="docker-compose"
else
    echo "오류: Docker Compose (V2 또는 V1)를 찾을 수 없습니다. 설치를 확인해주세요."
    exit 1
fi

# 1. 기존 Docker 리소스 정리
echo ""
echo "[1/5] 기존 Docker 서비스 및 볼륨 정리 시도..."
$COMPOSE_CMD down -v --remove-orphans 2>/dev/null || echo "INFO: 정리할 기존 Docker 서비스/볼륨이 없거나, 이미 정리되었을 수 있습니다 (무시하고 진행)."
echo "INFO: 기존 Docker 리소스 정리 완료 (또는 시도 완료)."

# 2. 로컬 SQLite DB 파일 삭제
DB_FILE_PATH="./db_files/food_nutrition_api.db"
echo ""
echo "[2/5] 기존 로컬 SQLite DB 파일($DB_FILE_PATH) 삭제 시도..."
if [ -f "$DB_FILE_PATH" ]; then
    rm -f "$DB_FILE_PATH"
    echo "INFO: 기존 로컬 SQLite DB 파일 삭제 완료."
else
    echo "INFO: 삭제할 기존 로컬 SQLite DB 파일이 없습니다."
fi

# 3. db_files 디렉토리 생성
DB_FILES_DIR="./db_files"
echo ""
echo "[3/5] '$DB_FILES_DIR' 디렉토리 확인 및 필요시 생성..."
if [ ! -d "$DB_FILES_DIR" ]; then
    mkdir -p "$DB_FILES_DIR"
    echo "INFO: '$DB_FILES_DIR' 디렉토리를 생성했습니다."
else
    echo "INFO: '$DB_FILES_DIR' 디렉토리가 이미 존재합니다."
fi

# 4. Docker Compose로 서비스 빌드 및 시작
echo ""
echo "[4/5] Docker Compose를 사용하여 서비스 빌드 및 시작 (백그라운드)..."
$COMPOSE_CMD up --build -d
echo "INFO: Docker 서비스 빌드 및 시작 요청 완료."

# Elasticsearch 서비스 Health 체크
echo "INFO: Elasticsearch 서비스 '$ES_SERVICE_NAME' Healthy 상태 대기 중... (최대 60초)"
COUNTER_ES=0
MAX_WAIT_ES=12 # 12 * 5초 = 60초
ES_IS_HEALTHY=false
while [ "$COUNTER_ES" -lt "$MAX_WAIT_ES" ]; do
    ES_CONTAINER_ID=$($COMPOSE_CMD ps -q "$ES_SERVICE_NAME" 2>/dev/null || echo "")
    if [ -n "$ES_CONTAINER_ID" ]; then
        HEALTH_STATUS=$(docker inspect --format='{{json .State.Health.Status}}' "$ES_CONTAINER_ID" 2>/dev/null || echo "\"unknown\"")
        if [ "$HEALTH_STATUS" = "\"healthy\"" ]; then
            echo "INFO: Elasticsearch 서비스 '$ES_SERVICE_NAME' (컨테이너 ID: $ES_CONTAINER_ID) (이)가 healthy 상태입니다."
            ES_IS_HEALTHY=true
            break
        fi
        echo "INFO: Elasticsearch 서비스 '$ES_SERVICE_NAME' (컨테이너 ID: $ES_CONTAINER_ID) 대기 중... ($((COUNTER_ES*5))초 경과, 현재 상태: $HEALTH_STATUS)"
    else
        echo "INFO: Elasticsearch 서비스 '$ES_SERVICE_NAME'의 컨테이너를 아직 찾을 수 없습니다. 대기 중... ($((COUNTER_ES*5))초 경과)"
    fi
    sleep 5
    COUNTER_ES=$((COUNTER_ES+1))
done

if [ "$ES_IS_HEALTHY" != true ]; then
    echo "경고: Elasticsearch 서비스 '$ES_SERVICE_NAME' (이)가 지정된 시간 내에 healthy 상태가 되지 않았습니다."
    echo "      데이터 로딩 스크립트의 ES 관련 작업이 실패할 수 있습니다."
    echo "      Elasticsearch 로그 확인: $COMPOSE_CMD logs $ES_SERVICE_NAME"
    # 이 시점에서 스크립트를 중단할지 여부는 정책에 따라 결정할 수 있습니다.
    # exit 1
fi

# FastAPI 앱 서비스 실행 확인
echo "INFO: FastAPI 애플리케이션 서비스 '$APP_SERVICE_NAME' 실행 대기 중... (최대 30초)"
COUNTER_APP=0
MAX_WAIT_APP=6 # 6 * 5초 = 30초
APP_IS_RUNNING=false
while [ "$COUNTER_APP" -lt "$MAX_WAIT_APP" ]; do
    APP_CONTAINER_ID=$($COMPOSE_CMD ps -q "$APP_SERVICE_NAME" 2>/dev/null || echo "")
    if [ -n "$APP_CONTAINER_ID" ]; then
        CONTAINER_STATUS=$(docker inspect --format='{{.State.Status}}' "$APP_CONTAINER_ID" 2>/dev/null || echo "unknown")
        if [ "$CONTAINER_STATUS" = "running" ]; then
            echo "INFO: FastAPI 애플리케이션 서비스 '$APP_SERVICE_NAME' (컨테이너 ID: $APP_CONTAINER_ID) (이)가 'running' 상태입니다."
            APP_IS_RUNNING=true
            break
        else
             echo "INFO: FastAPI 애플리케이션 서비스 '$APP_SERVICE_NAME' (컨테이너 ID: $APP_CONTAINER_ID)의 현재 상태는 '$CONTAINER_STATUS' 입니다. 'running' 상태 대기 중..."
        fi
    else
        echo "INFO: FastAPI 애플리케이션 서비스 '$APP_SERVICE_NAME'의 컨테이너를 아직 찾을 수 없습니다. 대기 중... ($((COUNTER_APP*5))초 경과)"
    fi
    sleep 5
    COUNTER_APP=$((COUNTER_APP+1))
done

if [ "$APP_IS_RUNNING" != true ]; then
    echo "오류: 애플리케이션 서비스 '$APP_SERVICE_NAME' (이)가 실행 중이지 않거나 'running' 상태가 아닙니다."
    echo "      FastAPI 앱 로그를 확인하세요: $COMPOSE_CMD logs $APP_SERVICE_NAME"
    exit 1
fi

# 5. Docker 컨테이너 내부에서 데이터 로딩 스크립트 실행
LOAD_SCRIPT_MODULE_PATH="scripts.load_data" # python -m 으로 실행할 모듈 경로
echo ""
echo "[5/5] Docker 컨테이너 내부에서 데이터 로딩 스크립트 실행 (모듈: $LOAD_SCRIPT_MODULE_PATH)..."
$COMPOSE_CMD exec "$APP_SERVICE_NAME" python -m "$LOAD_SCRIPT_MODULE_PATH"
echo "INFO: 데이터 로딩 스크립트 실행 완료. 위 로그에서 상세 내용을 확인하세요."

echo ""
echo "======================================================"
echo " 모든 설정 및 데이터 로딩 작업이 완료되었습니다! "
echo "======================================================"
echo ""
echo "FastAPI 애플리케이션 접속 정보:"
echo " - API 서버: http://localhost:8000"
echo " - Swagger UI (API 문서): http://localhost:8000/docs"
echo " - ReDoc (API 문서): http://localhost:8000/redoc"
echo ""
echo "Elasticsearch 직접 접속 정보 (필요시):"
echo " - Elasticsearch: http://localhost:9200"
echo " - 예시 (인덱스 문서 수 확인): curl -X GET \"http://localhost:9200/${FOOD_NUTRITIONS_INDEX_NAME:-food_nutritions_idx}/_count?pretty\"" # FOOD_NUTRITIONS_INDEX_NAME 변수가 없으면 기본값 사용
echo ""
echo "실행 중인 서비스 로그 확인:"
echo " - FastAPI 앱 로그: $COMPOSE_CMD logs -f $APP_SERVICE_NAME"
echo " - Elasticsearch 로그: $COMPOSE_CMD logs -f $ES_SERVICE_NAME"
echo ""
echo "서비스 중지:"
echo " - $COMPOSE_CMD down"
echo "======================================================"

exit 0