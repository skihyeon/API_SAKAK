from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.schemas.food_nutrition import FoodNutrition, FoodNutritionCreate, FoodNutritionUpdate

API_V1_STR = "/api/v1/food-nutritions"

def test_create_food_nutrition(client: TestClient):
    response = client.post(
        f"{API_V1_STR}",
        json={
            "food_cd": "API_TEST001",
            "food_name": "API 테스트 식품",
            "research_year": "2025",
            "maker_name": "API 테스트 제조사",
            "calorie": 150.0,
            "protein": 10.5,
            "province": 0.5,
            "sugars": 1,
            "salt": 700,
            "cholesterol": 0,
            "saturated_fatty_acids": 0.1,
            "trans_fat": 0,
            "id": 1
        },
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["food_cd"] == "API_TEST001"
    assert data["food_name"] == "API 테스트 식품"
    assert "id" in data
    food_nutrition_id = data["id"]

    response_duplicate = client.post(
        f"{API_V1_STR}",
        json={
            "food_cd": "API_TEST001",
            "food_name": "API 테스트 식품 중복",
        },
    )
    assert response_duplicate.status_code == 400, response_duplicate.text

def test_read_food_nutrition(client: TestClient):
    response_create = client.post(
        f"{API_V1_STR}",
        json={"food_cd": "API_READ001", "food_name": "API 조회용 식품"}
    )
    assert response_create.status_code == 201
    created_data = response_create.json()
    food_nutrition_id = created_data["id"]

    response_read = client.get(f"{API_V1_STR}/{food_nutrition_id}")
    assert response_read.status_code == 200, response_read.text
    data = response_read.json()
    assert data["id"] == food_nutrition_id
    assert data["food_cd"] == "API_READ001" 
    assert data["food_name"] == "API 조회용 식품"

    response_not_found = client.get(f"{API_V1_STR}/99999")
    assert response_not_found.status_code == 404, response_not_found.text

def test_read_food_nutritions(client: TestClient):
    client.post(f"{API_V1_STR}", json={"food_cd": "API_LIST001", "food_name": "목록1"})
    client.post(f"{API_V1_STR}", json={"food_cd": "API_LIST002", "food_name": "목록2"})

    response = client.get(f"{API_V1_STR}")
    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data) >= 2

def test_update_food_nutrition(client: TestClient):
    response_create = client.post(
        f"{API_V1_STR}",
        json={"food_cd": "API_UPDATE001", "food_name": "API 수정 전 식품", "calorie": 100.0}
    )
    assert response_create.status_code == 201
    created_data = response_create.json()
    food_nutrition_id = created_data["id"]

    response_update = client.put(
        f"{API_V1_STR}/{food_nutrition_id}",
        json={"food_name": "API 수정 후 식품", "calorie": 120.5}
    )
    assert response_update.status_code == 200, response_update.text
    data = response_update.json()
    assert data["id"] == food_nutrition_id
    assert data["food_name"] == "API 수정 후 식품"
    assert data["calorie"] == 120.5
    assert data["food_cd"] == "API_UPDATE001"

    response_not_found = client.put(
        f"{API_V1_STR}/99999",
        json={"food_name": "존재하지 않음"}
    )
    assert response_not_found.status_code == 404, response_not_found.text

def test_delete_food_nutrition(client: TestClient):
    response_create = client.post(
        f"{API_V1_STR}",
        json={"food_cd": "API_DELETE001", "food_name": "API 삭제용 식품"}
    )
    assert response_create.status_code == 201
    created_data = response_create.json()
    food_nutrition_id = created_data["id"]

    response_delete = client.delete(f"{API_V1_STR}/{food_nutrition_id}")
    assert response_delete.status_code == 200, response_delete.text 

    response_read_after_delete = client.get(f"{API_V1_STR}/{food_nutrition_id}")
    assert response_read_after_delete.status_code == 404, response_read_after_delete.text

    response_not_found = client.delete(f"{API_V1_STR}/99999")
    assert response_not_found.status_code == 404, response_not_found.text
    

def test_search_food_nutrition_by_food_name(client: TestClient):
    response = client.get(f"{API_V1_STR}/search/", params={"food_name": "김치"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
    if data:
        for item in data:
            assert "김치" in item.get("food_name", "")
            assert "food_cd" in item

def test_search_food_nutrition_by_food_code(client: TestClient):
    target_food_cd = "D000006"
    response = client.get(f"{API_V1_STR}/search/", params={"food_code": target_food_cd})
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
    if data:
        assert any(item.get("food_cd") == target_food_cd for item in data)

def test_search_food_nutrition_by_research_year(client: TestClient):
    target_year = "2023"
    response = client.get(f"{API_V1_STR}/search/", params={"research_year": target_year})
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
    if data:
        for item in data:
            assert item.get("research_year") == target_year

def test_search_food_nutrition_by_maker_name(client: TestClient):
    target_maker = "삼삼한밥상"
    response = client.get(f"{API_V1_STR}/search/", params={"maker_name": target_maker})
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
    if data:
        for item in data:
            assert target_maker in item.get("maker_name", "")

def test_search_food_nutrition_combined_filters(client: TestClient):
    params = {
        "food_name": "무말랭이 김치",
        "maker_name": "삼삼한밥상",
        "research_year": "2018",
        "food_code": "D018604"
    }
    response = client.get(f"{API_V1_STR}/search/", params=params)
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    if data:
        item = data[0]
        assert "무말랭이 김치" in item.get("food_name", "")
        assert "삼삼한밥상" in item.get("maker_name", "")
        assert item.get("research_year") == "2018"
        assert item.get("food_cd") == "D018604"

def test_search_food_nutrition_pagination(client: TestClient):
    response_limit_1 = client.get(f"{API_V1_STR}/search/", params={"limit": 1})
    assert response_limit_1.status_code == 200
    data_limit_1 = response_limit_1.json()
    assert isinstance(data_limit_1, list)
    assert len(data_limit_1) <= 1 

    if len(data_limit_1) == 1: 
        first_item_id = data_limit_1[0]["id"]
        response_skip_1_limit_1 = client.get(f"{API_V1_STR}/search/", params={"skip": 1, "limit": 1})
        assert response_skip_1_limit_1.status_code == 200
        data_skip_1_limit_1 = response_skip_1_limit_1.json()
        assert isinstance(data_skip_1_limit_1, list)
        if data_skip_1_limit_1: 
             assert len(data_skip_1_limit_1) <= 1
             assert data_skip_1_limit_1[0]["id"] != first_item_id

def test_search_food_nutrition_no_results(client: TestClient):
    response = client.get(f"{API_V1_STR}/search/", params={"food_name": "이런음식은절대없을거야12345"})
    assert response.status_code == 200, response.text 
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0 

def test_search_food_nutrition_no_params(client: TestClient):
    response = client.get(f"{API_V1_STR}/search/")
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)