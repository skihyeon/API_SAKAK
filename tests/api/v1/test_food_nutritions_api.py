from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.schemas.food_nutrition import FoodNutrition, FoodNutritionCreate, FoodNutritionUpdate

API_V1_STR = "/api/v1"

def test_create_food_nutrition(client: TestClient):
    response = client.post(
        f"{API_V1_STR}/food-nutritions/",
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
        f"{API_V1_STR}/food-nutritions/",
        json={
            "food_cd": "API_TEST001",
            "food_name": "API 테스트 식품 중복",
        },
    )
    assert response_duplicate.status_code == 400, response_duplicate.text

def test_read_food_nutrition(client: TestClient):
    response_create = client.post(
        f"{API_V1_STR}/food-nutritions/",
        json={"food_cd": "API_READ001", "food_name": "API 조회용 식품"}
    )
    assert response_create.status_code == 201
    created_data = response_create.json()
    food_nutrition_id = created_data["id"]

    response_read = client.get(f"{API_V1_STR}/food-nutritions/{food_nutrition_id}")
    assert response_read.status_code == 200, response_read.text
    data = response_read.json()
    assert data["id"] == food_nutrition_id
    assert data["food_cd"] == "API_READ001" 
    assert data["food_name"] == "API 조회용 식품"

    response_not_found = client.get(f"{API_V1_STR}/food-nutritions/99999")
    assert response_not_found.status_code == 404, response_not_found.text

def test_read_food_nutritions(client: TestClient):
    client.post(f"{API_V1_STR}/food-nutritions/", json={"food_cd": "API_LIST001", "food_name": "목록1"})
    client.post(f"{API_V1_STR}/food-nutritions/", json={"food_cd": "API_LIST002", "food_name": "목록2"})

    response = client.get(f"{API_V1_STR}/food-nutritions/")
    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data) >= 2

def test_update_food_nutrition(client: TestClient):
    response_create = client.post(
        f"{API_V1_STR}/food-nutritions/",
        json={"food_cd": "API_UPDATE001", "food_name": "API 수정 전 식품", "calorie": 100.0}
    )
    assert response_create.status_code == 201
    created_data = response_create.json()
    food_nutrition_id = created_data["id"]

    response_update = client.put(
        f"{API_V1_STR}/food-nutritions/{food_nutrition_id}",
        json={"food_name": "API 수정 후 식품", "calorie": 120.5}
    )
    assert response_update.status_code == 200, response_update.text
    data = response_update.json()
    assert data["id"] == food_nutrition_id
    assert data["food_name"] == "API 수정 후 식품"
    assert data["calorie"] == 120.5
    assert data["food_cd"] == "API_UPDATE001"

    response_not_found = client.put(
        f"{API_V1_STR}/food-nutritions/99999",
        json={"food_name": "존재하지 않음"}
    )
    assert response_not_found.status_code == 404, response_not_found.text

def test_delete_food_nutrition(client: TestClient):
    response_create = client.post(
        f"{API_V1_STR}/food-nutritions/",
        json={"food_cd": "API_DELETE001", "food_name": "API 삭제용 식품"}
    )
    assert response_create.status_code == 201
    created_data = response_create.json()
    food_nutrition_id = created_data["id"]

    response_delete = client.delete(f"{API_V1_STR}/food-nutritions/{food_nutrition_id}")
    assert response_delete.status_code == 200, response_delete.text 

    response_read_after_delete = client.get(f"{API_V1_STR}/food-nutritions/{food_nutrition_id}")
    assert response_read_after_delete.status_code == 404, response_read_after_delete.text

    response_not_found = client.delete(f"{API_V1_STR}/food-nutritions/99999")
    assert response_not_found.status_code == 404, response_not_found.text