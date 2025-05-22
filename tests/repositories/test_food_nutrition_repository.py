import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.repositories import food_nutrition_repository
from app.models.food_nutrition import FoodNutrition as FoodNutritionModel
from app.schemas.food_nutrition import FoodNutritionCreate, FoodNutritionUpdate
from app.db.session import Base 

SQLALCHEMY_DATABASE_URL_TEST = "sqlite:///:memory:"

engine_test = create_engine(
    SQLALCHEMY_DATABASE_URL_TEST, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)

@pytest.fixture(scope="function")
def db_session() -> Session:
    Base.metadata.create_all(bind=engine_test)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine_test)

def test_create_food_nutrition(db_session: Session):
    food_nutrition_data = FoodNutritionCreate(
        food_cd="TEST001",
        food_name="테스트 식품",
        research_year="2024",
        maker_name="테스트 제조사",
    )
    created_food = food_nutrition_repository.create_food_nutrition(db=db_session, food_nutrition=food_nutrition_data)

    assert created_food is not None
    assert created_food.food_cd == "TEST001"
    assert created_food.food_name == "테스트 식품"
    assert created_food.id is not None

def test_get_food_nutrition(db_session: Session):
    food_nutrition_data = FoodNutritionCreate(food_cd="TEST002", food_name="조회용 식품")
    created_food = food_nutrition_repository.create_food_nutrition(db=db_session, food_nutrition=food_nutrition_data)

    retrieved_food = food_nutrition_repository.get_food_nutrition(db=db_session, food_nutrition_id=created_food.id)
    assert retrieved_food is not None
    assert retrieved_food.id == created_food.id
    assert retrieved_food.food_name == "조회용 식품"

    non_existent_food = food_nutrition_repository.get_food_nutrition(db=db_session, food_nutrition_id=999)
    assert non_existent_food is None

def test_get_food_nutrition_by_food_cd(db_session: Session):
    food_nutrition_data = FoodNutritionCreate(food_cd="UNIQUECD01", food_name="고유코드식품")
    food_nutrition_repository.create_food_nutrition(db=db_session, food_nutrition=food_nutrition_data)

    retrieved_food = food_nutrition_repository.get_food_nutrition_by_food_cd(db=db_session, food_cd="UNIQUECD01")
    assert retrieved_food is not None
    assert retrieved_food.food_name == "고유코드식품"

    non_existent_food = food_nutrition_repository.get_food_nutrition_by_food_cd(db=db_session, food_cd="NONEXISTENTCD")
    assert non_existent_food is None

def test_get_food_nutritions(db_session: Session):
    food_nutrition_repository.create_food_nutrition(db=db_session, food_nutrition=FoodNutritionCreate(food_cd="LIST001", food_name="목록 식품 1"))
    food_nutrition_repository.create_food_nutrition(db=db_session, food_nutrition=FoodNutritionCreate(food_cd="LIST002", food_name="목록 식품 2"))

    all_foods = food_nutrition_repository.get_food_nutritions(db=db_session)
    assert len(all_foods) == 2

    limited_foods = food_nutrition_repository.get_food_nutritions(db=db_session, limit=1)
    assert len(limited_foods) == 1

    skipped_foods = food_nutrition_repository.get_food_nutritions(db=db_session, skip=1, limit=1)
    assert len(skipped_foods) == 1
    assert skipped_foods[0].food_cd == "LIST002" 

def test_update_food_nutrition(db_session: Session):
    food_nutrition_data = FoodNutritionCreate(food_cd="UPDATE001", food_name="수정 전 식품")
    created_food = food_nutrition_repository.create_food_nutrition(db=db_session, food_nutrition=food_nutrition_data)

    update_data = FoodNutritionUpdate(food_name="수정된 식품명", maker_name="새로운 제조사")
    updated_food = food_nutrition_repository.update_food_nutrition(
        db=db_session, food_nutrition_id=created_food.id, food_nutrition_update=update_data
    )

    assert updated_food is not None
    assert updated_food.food_name == "수정된 식품명"
    assert updated_food.maker_name == "새로운 제조사"
    assert updated_food.food_cd == "UPDATE001" 

    non_existent_update = food_nutrition_repository.update_food_nutrition(
        db=db_session, food_nutrition_id=999, food_nutrition_update=update_data
    )
    assert non_existent_update is None

def test_delete_food_nutrition(db_session: Session):
    food_nutrition_data = FoodNutritionCreate(food_cd="DELETE001", food_name="삭제될 식품")
    created_food = food_nutrition_repository.create_food_nutrition(db=db_session, food_nutrition=food_nutrition_data)


    deleted_food_marker = food_nutrition_repository.delete_food_nutrition(db=db_session, food_nutrition_id=created_food.id)
    assert deleted_food_marker is not None 
    assert deleted_food_marker.id == created_food.id

    retrieved_after_delete = food_nutrition_repository.get_food_nutrition(db=db_session, food_nutrition_id=created_food.id)
    assert retrieved_after_delete is None

    non_existent_delete = food_nutrition_repository.delete_food_nutrition(db=db_session, food_nutrition_id=999)
    assert non_existent_delete is None