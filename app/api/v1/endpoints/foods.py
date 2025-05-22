from fastapi import APIRouter, HTTPException, status
from typing import List
from app.schemas.food import Food

router = APIRouter()

mock_db_foods = [
    Food(id=1, food_cd="01", food_name="test_food_name1", maker_name="test_maker_name1"),
    Food(id=2, food_cd="02", food_name="test_food_name2", maker_name="test_maker_name2"),
    Food(id=3, food_cd="03", food_name="test_food_name3", maker_name="test_maker_name3"),
]


@router.get("/", response_model=List[Food], summary="음식 목록 조회 (Mock)")
async def read_foods(skip: int = 0, limit: int = 10):
    """
    등록된 음식 정보 목록을 조회합니다. (현재 Mock 데이터 반환)
    - **skip**: 건너뛸 항목 수
    - **limit**: 반환할 최대 항목 수
    """
    return mock_db_foods[skip : skip + limit]

@router.get("/{food_id}", response_model=Food, summary="특정 음식 상세 조회 (Mock)")
async def read_food(food_id: int):
    """
    지정된 ID의 음식 상세 정보를 조회합니다. (현재 Mock 데이터 반환)
    - **food_id**: 조회할 음식의 고유 ID
    """
    for food_item in mock_db_foods:
        if food_item.id == food_id:
            return food_item
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Food with id {food_id} not found")
