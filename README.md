# 식품영양정보 API (Food Nutrition API)

## 1. Project Setup

`setup_project.sh` 스크립트를 통해 별도 설정없이 한 번에 배포 가능합니다.

**사전 요구 사항:**
* Docker
* Docker Compose

**실행 방법:**
1.  Git 리포지토리 클론:
    ```bash
    git clone https://github.com/skihyeon/API_SAKAK.git
    cd API_SAKAK
    ```
2.  `setup_project.sh` 스크립트에 실행 권한 부여:
    ```bash
    chmod +x setup_project.sh
    ```
3.  스크립트 실행:
    ```bash
    ./setup_project.sh
    ```
    스크립트 실행이 완료되면 FastAPI 애플리케이션과 Elasticsearch가 실행되며, 초기 데이터 로딩까지 완료됩니다.

## 2. 기술 스택

* **언어:** Python 3.10+
* **프레임워크:** FastAPI
* **데이터베이스:** SQLite (주 저장소), Elasticsearch 7.10.1 (검색 엔진)
* **DB 마이그레이션:** Alembic
* **의존성 관리:** pip + `requirements.txt`
* **실행 환경:** Docker, Docker Compose

## 3. API 접속 정보 

* **API 서버 기본 URL:** `http://localhost:8000`
* **Swagger UI (대화형 API 문서):** `http://localhost:8000/docs`
* **ReDoc (대안 API 문서):** `http://localhost:8000/redoc`

---