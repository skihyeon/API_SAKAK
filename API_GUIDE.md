# 식품영양정보 API 가이드

## 1. 개요 (Overview)

본 문서는 **식품영양정보 API**의 사용 방법을 안내합니다. 이 API는 식품 영양 정보를 조회, 생성, 수정, 삭제하고 다양한 조건으로 검색하는 RESTful 인터페이스를 제공합니다.

* **기본 Base URL:** `http://localhost:8000`
* **API 버전 접두사:** `/api/v1`

따라서 모든 API 요청의 기본 경로는 `http://localhost:8000/api/v1`이 됩니다.


## 2. 요청/응답 형식 (Request/Response Format)

* **데이터 형식:** 모든 요청 본문(Request Body)과 응답 본문(Response Body)은 **JSON (`application/json`)** 형식을 사용합니다.
* **성공 응답:** 일반적으로 요청이 성공하면 해당 작업의 결과 데이터와 함께 HTTP `2xx` 상태 코드가 반환됩니다.
* **에러 응답:** 요청 처리 중 오류 발생 시, 주로 다음과 같은 JSON 형식의 에러 메시지와 함께 HTTP `4xx` 또는 `5xx` 상태 코드가 반환됩니다:
    ```json
    {
      "detail": "오류 상세 메시지"
    }
    ```

## 4. HTTP 상태 코드 (HTTP Status Codes)

본 API에서 주로 사용되는 HTTP 상태 코드와 그 의미는 다음과 같습니다:

* **`200 OK`**: 요청이 성공적으로 처리되었으며, 주로 `GET` (조회), `PUT` (수정), `DELETE` (삭제 성공 시 삭제된 객체와 함께) 요청에 대한 응답입니다.
* **`201 Created`**: 새로운 리소스가 성공적으로 생성되었음을 나타냅니다 (`POST` 요청 성공 시).
* **`400 Bad Request`**: 클라이언트의 요청이 잘못되었거나 서버가 이해할 수 없는 요청일 때 반환됩니다 (예: `food_cd` 중복 생성 시도).
* **`404 Not Found`**: 요청한 리소스를 서버에서 찾을 수 없을 때 반환됩니다.
* **`422 Unprocessable Entity`**: 요청 본문의 내용은 이해했지만, 의미론적으로 유효하지 않아 처리할 수 없을 때 반환됩니다 (주로 FastAPI의 데이터 유효성 검사 실패 시).
* **`500 Internal Server Error`**: 서버 내부 처리 중 예기치 않은 오류가 발생했을 때 반환됩니다.
* **`503 Service Unavailable`**: 일시적으로 서비스를 사용할 수 없을 때 반환됩니다 (예: Search API가 Elasticsearch에 연결할 수 없는 경우).

## 5. API 엔드포인트 상세

### 5.1. 음식 영양 정보 (`/food-nutritions`)

#### 5.1.1. 새로운 음식 영양 정보 생성

* **설명:** 새로운 음식 영양 정보를 시스템에 등록합니다. `food_cd` (식품코드)는 고유해야 합니다.
* **Method:** `POST`
* **URL:** `/api/v1/food-nutritions/`
* **Request Body (`application/json`):** (`FoodNutritionCreate` 스키마)
    * `food_cd` (string, 필수): 식품코드
    * `food_name` (string, 필수): 식품이름
    * `group_name` (string, 선택): 식품군 ({식품대분류} - {식품상세분류})
    * `research_year` (string, 선택): 조사년도 (YYYY)
    * `maker_name` (string, 선택): 지역/제조사
    * `ref_name` (string, 선택): 자료출처 (예: "식약처('23)")
    * `serving_size` (float, 선택): 1회 제공량(g)
    * `calorie` (float, 선택): 열량(kcal)
    * `carbohydrate` (float, 선택): 탄수화물(g)
    * `protein` (float, 선택): 단백질(g)
    * `province` (float, 선택): 지방(g)
    * `sugars` (float, 선택): 총당류(g)
    * `salt` (float, 선택): 나트륨(mg)
    * `cholesterol` (float, 선택): 콜레스테롤(mg)
    * `saturated_fatty_acids` (float, 선택): 포화지방산(g)
    * `trans_fat` (float, 선택): 트랜스지방(g). 
    ** "1g 미만"의 경우 `-1.0`으로 입력됩니다. **
* **예시 요청 (`curl`):**
    ```bash
    curl -X POST "http://localhost:8000/api/v1/food-nutritions/" \
    -H "accept: application/json" \
    -H "Content-Type: application/json" \
    -d '{
      "food_cd": "NEW001",
      "food_name": "새로운 테스트 식품",
      "group_name": "테스트군",
      "research_year": "2025",
      "maker_name": "본인",
      "calorie": 123.4,
      "protein": 10.1
    }'
    ```
* **성공 응답:** `201 Created`
    * **Body:** 생성된 음식 영양 정보 (`FoodNutrition` 스키마)
        ```json
        {
          "food_cd": "NEW001",
          "food_name": "새로운 테스트 식품",
          "group_name": "테스트군",
          "research_year": "2025",
          "maker_name": "본인",
          "ref_name": null,
          "serving_size": null,
          "calorie": 123.4,
          "carbohydrate": null,
          "protein": 10.1,
          "province": null,
          "sugars": null,
          "salt": null,
          "cholesterol": null,
          "saturated_fatty_acids": null,
          "trans_fat": null,
          "id": 1  // 예시 ID (실제로는 DB에서 자동 생성)
        }
        ```
* **주요 오류 응답:** `400 Bad Request` (예: `food_cd` 중복), `422 Unprocessable Entity` (요청 데이터 유효성 오류).

#### 5.1.2. 음식 영양 정보 목록 조회

* **설명:** 등록된 음식 영양 정보 전체 목록을 페이지네이션하여 조회합니다.
* **Method:** `GET`
* **URL:** `/api/v1/food-nutritions/`
* **Query Parameters:**
    * `skip` (integer, 선택, 기본값: 0): 건너뛸 항목 수.
    * `limit` (integer, 선택, 기본값: 100): 반환할 최대 항목 수.
* **예시 요청 (`curl`):**
    ```bash
    curl -X GET "http://localhost:8000/api/v1/food-nutritions/?skip=0&limit=2" \
    -H "accept: application/json"
    ```
* **성공 응답:** `200 OK`
    * **Body:** 음식 영양 정보 객체의 리스트 (`List[FoodNutrition]`)

#### 5.1.3. 특정 음식 영양 정보 상세 조회

* **설명:** 지정된 `id`를 가진 음식 영양 정보의 상세 내용을 조회합니다.
* **Method:** `GET`
* **URL:** `/api/v1/food-nutritions/{food_nutrition_id}`
* **Path Parameters:**
    * `food_nutrition_id` (integer, 필수): 조회할 음식 영양 정보의 고유 ID.
* **예시 요청 (`curl`):**
    ```bash
    curl -X GET "http://localhost:8000/api/v1/food-nutritions/1" \
    -H "accept: application/json"
    ```
* **성공 응답:** `200 OK`
    * **Body:** 특정 음식 영양 정보 객체 (`FoodNutrition`)
* **주요 오류 응답:** `404 Not Found`.

#### 5.1.4. 특정 음식 영양 정보 수정

* **설명:** 지정된 `id`를 가진 음식 영양 정보의 내용을 수정합니다. 부분 수정(일부 필드만 변경)을 지원합니다.
* **Method:** `PUT`
* **URL:** `/api/v1/food-nutritions/{food_nutrition_id}`
* **Path Parameters:**
    * `food_nutrition_id` (integer, 필수): 수정할 음식 영양 정보의 고유 ID.
* **Request Body (`application/json`):** (`FoodNutritionUpdate` 스키마 - 모든 필드가 선택 사항)
* **예시 요청 (`curl`):**
    ```bash
    curl -X PUT "http://localhost:8000/api/v1/food-nutritions/1" \
    -H "accept: application/json" \
    -H "Content-Type: application/json" \
    -d '{
      "food_name": "수정된 식품 이름",
      "calorie": 150.0
    }'
    ```
* **성공 응답:** `200 OK`
    * **Body:** 수정된 음식 영양 정보 객체 (`FoodNutrition`)
* **주요 오류 응답:** `404 Not Found`, `400 Bad Request` (예: `food_cd` 중복), `422 Unprocessable Entity`.

#### 5.1.5. 특정 음식 영양 정보 삭제

* **설명:** 지정된 `id`를 가진 음식 영양 정보를 삭제합니다.
* **Method:** `DELETE`
* **URL:** `/api/v1/food-nutritions/{food_nutrition_id}`
* **Path Parameters:**
    * `food_nutrition_id` (integer, 필수): 삭제할 음식 영양 정보의 고유 ID.
* **예시 요청 (`curl`):**
    ```bash
    curl -X DELETE "http://localhost:8000/api/v1/food-nutritions/1" \
    -H "accept: application/json"
    ```
* **성공 응답:** `200 OK` (현재 구현은 삭제된 객체 정보를 반환합니다. 더 RESTful한 방식은 `204 No Content`와 빈 본문입니다.)
    * **Body:** (현재 구현 기준) 삭제된 음식 영양 정보 객체 (`FoodNutrition`)
* **주요 오류 응답:** `404 Not Found`.

#### 5.1.6. 음식 영양 정보 검색 (Elasticsearch)

* **설명:** 다양한 조건으로 음식 영양 정보를 Elasticsearch에서 검색합니다. 모든 조건은 AND로 조합됩니다.
* **Method:** `GET`
* **URL:** `/api/v1/food-nutritions/search/`
* **Query Parameters:**
    * `food_name: Optional[str]` - 검색할 식품 이름 (부분 일치).
    * `research_year: Optional[str]` - 조사년도 (YYYY, 정확히 일치).
    * `maker_name: Optional[str]` - 지역/제조사 (부분 일치).
    * `food_code: Optional[str]` - 식품코드 (DB의 `food_cd`와 정확히 일치).
    * `skip: int = 0` - 건너뛸 결과 수 (페이지네이션).
    * `limit: int = 10` - 반환할 최대 결과 수 (페이지네이션, 기본값 10, 최대 100).
* **주의사항:** 영양성분 값 중 `-1.0`으로 표시되는 것은 원본 데이터에서 "1g 미만"을 의미합니다.
* **예시 요청 (`curl`):**
    ```bash
    curl -X GET "http://localhost:8000/api/v1/food-nutritions/search/?food_name=김치&maker_name=종가집&limit=5" \
    -H "accept: application/json"
    ```
* **성공 응답:** `200 OK`
    * **Body:** 검색된 음식 영양 정보 객체의 리스트 (`List[FoodNutritionSearchResponse]`). 각 객체는 "출력 항목" 표에 명시된 17개 필드를 포함합니다.

## 6. 참고한 RESTful API 모범 사례

[모범사례](https://thebasics.tistory.com/164)

본 API는 다음과 같은 RESTful 디자인 원칙을 준수하여 설계되었습니다:

* **자원(Resource) 중심의 URI 설계:** URI는 행위보다는 명사(예: `/food-nutritions`)를 사용하여 자원을 명확히 표현합니다.
* **HTTP 메소드의 의미론적 사용:** `GET` (조회), `POST` (생성), `PUT` (전체 수정 또는 생성), `DELETE` (삭제) 등 HTTP 메소드를 각 연산의 의미에 맞게 사용합니다.
* **적절한 HTTP 상태 코드 활용:** 요청 처리 결과를 명확히 나타내는 표준 HTTP 상태 코드를 반환하여 클라이언트가 API의 상태를 이해하기 쉽도록 합니다.
* **Stateless (무상태성):** 각 API 요청은 이전 요청과 독립적으로 처리되며, 서버는 클라이언트의 세션 상태를 유지하지 않습니다.
* **JSON 형식 사용:** 요청과 응답의 본문은 웹에서 널리 사용되는 표준 형식인 JSON을 사용합니다.
* **Richardson Maturity Model (RMM) 고려:** 본 API는 주로 RMM Level 2 (자원, HTTP 동사, 상태 코드의 의미있는 사용)를 목표로 구현되었습니다. 또한 FastAPI의 자동 문서 생성 기능(/docs, /redoc)을 통해 API 명세를 쉽게 확인하고 테스트할 수 있도록 지원합니다.