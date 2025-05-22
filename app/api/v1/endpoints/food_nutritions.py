from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional


from app.schemas.food_nutrition import (
    FoodNutrition,
    FoodNutritionCreate,
    FoodNutritionUpdate,
    FoodNutritionSearchResponse
)

from app.repositories import food_nutrition_repository
from app.search import get_es_client, search_food_nutritions_in_es 
from elasticsearch import Elasticsearch

from app.db.session import get_db

router = APIRouter()

@router.post("/", response_model=FoodNutrition, status_code=status.HTTP_201_CREATED, summary="새로운 음식 영양 정보 생성")
async def create_new_food_nutrition(
    food_nutrition_in: FoodNutritionCreate,
    db: Session = Depends(get_db)
):
    db_food_nutrition_with_food_cd = food_nutrition_repository.get_food_nutrition_by_food_cd(db, food_cd=food_nutrition_in.food_cd)
    if db_food_nutrition_with_food_cd:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"FoodNutrition with food_cd '{food_nutrition_in.food_cd}' already exists."
        )
    created_food_nutrition = food_nutrition_repository.create_food_nutrition(db=db, food_nutrition=food_nutrition_in)
    return created_food_nutrition

@router.get("/{food_nutrition_id}", response_model=FoodNutrition, summary="특정 음식 영양 정보 상세 조회")
async def read_single_food_nutrition(
    food_nutrition_id: int,
    db: Session = Depends(get_db)
):
    db_food_nutrition = food_nutrition_repository.get_food_nutrition(db=db, food_nutrition_id=food_nutrition_id)
    if db_food_nutrition is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"FoodNutrition with id {food_nutrition_id} not found")
    return db_food_nutrition

@router.get("/", response_model=List[FoodNutrition], summary="음식 영양 정보 목록 조회")
async def read_all_food_nutritions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    food_nutritions = food_nutrition_repository.get_food_nutritions(db=db, skip=skip, limit=limit)
    return food_nutritions

@router.put("/{food_nutrition_id}", response_model=FoodNutrition, summary="특정 음식 영양 정보 수정")
async def update_existing_food_nutrition(
    food_nutrition_id: int,
    food_nutrition_in: FoodNutritionUpdate,
    db: Session = Depends(get_db)
):
    db_food_nutrition = food_nutrition_repository.get_food_nutrition(db, food_nutrition_id=food_nutrition_id)
    if db_food_nutrition is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"FoodNutrition with id {food_nutrition_id} not found to update")

    if food_nutrition_in.food_cd and food_nutrition_in.food_cd != db_food_nutrition.food_cd:
        existing_food_cd = food_nutrition_repository.get_food_nutrition_by_food_cd(db, food_cd=food_nutrition_in.food_cd)
        if existing_food_cd and existing_food_cd.id != food_nutrition_id : 
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"FoodNutrition with food_cd '{food_nutrition_in.food_cd}' already exists."
            )

    updated_food_nutrition = food_nutrition_repository.update_food_nutrition(
        db=db, food_nutrition_id=food_nutrition_id, food_nutrition_update=food_nutrition_in
    )
    return updated_food_nutrition

@router.delete("/{food_nutrition_id}", response_model=FoodNutrition, summary="특정 음식 영양 정보 삭제")
async def delete_single_food_nutrition(
    food_nutrition_id: int,
    db: Session = Depends(get_db)
):
    """
    지정된 ID의 음식 영양 정보를 삭제합니다.
    - **food_nutrition_id**: 삭제할 음식 영양 정보의 고유 ID
    """
    deleted_food_nutrition = food_nutrition_repository.delete_food_nutrition(db=db, food_nutrition_id=food_nutrition_id)
    if deleted_food_nutrition is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"FoodNutrition with id {food_nutrition_id} not found to delete")
    return deleted_food_nutrition


@router.get("/search/", response_model=List[FoodNutritionSearchResponse], summary="음식 영양 정보 검색")
async def search_food_nutritions_via_es(
    food_name: Optional[str] = Query(None, description="검색할 식품 이름 (부분 일치)"),
    research_year: Optional[str] = Query(None, description="조사년도 (YYYY)"),
    maker_name: Optional[str] = Query(None, description="지역/제조사 (부분 일치)"),
    food_code: Optional[str] = Query(None, description="식품코드"),
    skip: int = Query(0, ge=0, description="건너뛸 결과 수"),
    limit: int = Query(10, ge=1, le=100, description="반환할 최대 결과 수"),
    es: Elasticsearch = Depends(get_es_client)
):
    """
    주어진 조건에 따라 Elasticsearch에서 음식 영양 정보를 검색합니다.
    - 모든 검색 조건은 AND로 조합됩니다.
    - `food_name`과 `maker_name`은 부분 일치 검색을 지원합니다.
    - `research_year`와 `food_code`는 정확히 일치하는 값을 찾습니다.
    """

    results = search_food_nutritions_in_es(
        es_client=es,
        food_name=food_name,
        research_year=research_year,
        maker_name=maker_name,
        food_cd=food_code,
        skip=skip,
        limit=limit
    )
    return results
