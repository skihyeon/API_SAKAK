import pytest
from sqlalchemy.orm import Session
from unittest.mock import patch, MagicMock 

from app.repositories import food_nutrition_repository
from app.models.food_nutrition import FoodNutrition as FoodNutritionModel
from app.schemas.food_nutrition import FoodNutritionCreate, FoodNutritionUpdate

from app.db.session import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.search.es_utils import FOOD_NUTRITIONS_INDEX_NAME


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

def test_get_food_nutrition(db_session: Session):
    food_data = FoodNutritionCreate(food_cd="GET001", food_name="조회용 식품 Repo")
    created_food = food_nutrition_repository.create_food_nutrition(db=db_session, food_nutrition=food_data)

    retrieved_food = food_nutrition_repository.get_food_nutrition(db=db_session, food_nutrition_id=created_food.id)
    assert retrieved_food is not None
    assert retrieved_food.id == created_food.id
    assert retrieved_food.food_name == "조회용 식품 Repo"

    non_existent_food = food_nutrition_repository.get_food_nutrition(db=db_session, food_nutrition_id=999)
    assert non_existent_food is None

def test_get_food_nutrition_by_food_cd(db_session: Session):
    food_data = FoodNutritionCreate(food_cd="GET_CD_001", food_name="CD 조회용 식품 Repo")
    food_nutrition_repository.create_food_nutrition(db=db_session, food_nutrition=food_data)

    retrieved_food = food_nutrition_repository.get_food_nutrition_by_food_cd(db=db_session, food_cd="GET_CD_001")
    assert retrieved_food is not None
    assert retrieved_food.food_name == "CD 조회용 식품 Repo"

def test_get_food_nutritions(db_session: Session):
    food_nutrition_repository.create_food_nutrition(db=db_session, food_nutrition=FoodNutritionCreate(food_cd="LIST_R_001", food_name="목록 Repo 1"))
    food_nutrition_repository.create_food_nutrition(db=db_session, food_nutrition=FoodNutritionCreate(food_cd="LIST_R_002", food_name="목록 Repo 2"))
    all_foods = food_nutrition_repository.get_food_nutritions(db=db_session)
    assert len(all_foods) >= 2


@patch('app.repositories.food_nutrition_repository.get_es_client')
def test_create_food_nutrition_with_es_sync(mock_get_es_client: MagicMock, db_session: Session):
    mock_es_instance = MagicMock()
    mock_es_instance.ping.return_value = True
    mock_get_es_client.return_value = mock_es_instance 

    food_create_data = FoodNutritionCreate(
        food_cd="ES_CREATE001",
        food_name="ES 동기화 생성 테스트 식품",
        research_year="2024"
    )

    created_food_model = food_nutrition_repository.create_food_nutrition(db=db_session, food_nutrition=food_create_data)

    assert created_food_model is not None
    assert created_food_model.food_cd == "ES_CREATE001"
    assert created_food_model.id is not None

    mock_get_es_client.assert_called_once() 
    mock_es_instance.ping.assert_called_once()
    
    expected_es_doc = food_nutrition_repository._get_es_doc_from_model(created_food_model)
    mock_es_instance.index.assert_called_once_with(
        index=FOOD_NUTRITIONS_INDEX_NAME,
        id=created_food_model.id,
        document=expected_es_doc,
        refresh="wait_for"
    )

@patch('app.repositories.food_nutrition_repository.get_es_client')
def test_update_food_nutrition_with_es_sync(mock_get_es_client: MagicMock, db_session: Session):
    mock_es_instance = MagicMock()
    mock_es_instance.ping.return_value = True
    mock_get_es_client.return_value = mock_es_instance

    initial_data = FoodNutritionCreate(food_cd="ES_UPDATE001", food_name="ES 수정 전", calorie=100.0)
    created_food_model = food_nutrition_repository.create_food_nutrition(db=db_session, food_nutrition=initial_data)
    
    mock_es_instance.reset_mock()
    mock_es_instance.ping.return_value = True

    food_update_data = FoodNutritionUpdate(food_name="ES 수정 후", calorie=150.5)
    updated_food_model = food_nutrition_repository.update_food_nutrition(
        db=db_session, food_nutrition_id=created_food_model.id, food_nutrition_update=food_update_data
    )

    assert updated_food_model is not None
    assert updated_food_model.food_name == "ES 수정 후"
    assert updated_food_model.calorie == 150.5

    mock_get_es_client.assert_called()
    assert mock_get_es_client.call_count >= 2
    mock_es_instance.ping.assert_called()
    
    expected_es_doc = food_nutrition_repository._get_es_doc_from_model(updated_food_model)
    mock_es_instance.index.assert_called_with(
        index=FOOD_NUTRITIONS_INDEX_NAME,
        id=updated_food_model.id,
        document=expected_es_doc,
        refresh="wait_for"
    )

@patch('app.repositories.food_nutrition_repository.get_es_client')
def test_delete_food_nutrition_with_es_sync(mock_get_es_client: MagicMock, db_session: Session):
    mock_es_instance = MagicMock()
    mock_es_instance.ping.return_value = True
    mock_get_es_client.return_value = mock_es_instance

    initial_data = FoodNutritionCreate(food_cd="ES_DELETE001", food_name="ES 삭제 대상")
    created_food_model = food_nutrition_repository.create_food_nutrition(db=db_session, food_nutrition=initial_data)
    
    mock_es_instance.reset_mock()
    mock_es_instance.ping.return_value = True

    deleted_item_id = created_food_model.id

    deleted_marker = food_nutrition_repository.delete_food_nutrition(db=db_session, food_nutrition_id=deleted_item_id)

    assert deleted_marker is not None
    assert food_nutrition_repository.get_food_nutrition(db=db_session, food_nutrition_id=deleted_item_id) is None

    mock_get_es_client.assert_called()
    mock_es_instance.ping.assert_called()
    mock_es_instance.delete.assert_called_once_with(
        index=FOOD_NUTRITIONS_INDEX_NAME,
        id=deleted_item_id,
        refresh="wait_for"
    )

@patch('app.repositories.food_nutrition_repository.get_es_client')
def test_create_food_nutrition_es_ping_fails(mock_get_es_client: MagicMock, db_session: Session):
    mock_es_instance = MagicMock()
    mock_es_instance.ping.return_value = False
    mock_get_es_client.return_value = mock_es_instance

    food_create_data = FoodNutritionCreate(food_cd="ES_PINGFAIL001", food_name="ES Ping 실패 테스트")
    created_food_model = food_nutrition_repository.create_food_nutrition(db=db_session, food_nutrition=food_create_data)

    assert created_food_model is not None
    assert created_food_model.food_cd == "ES_PINGFAIL001"

    mock_get_es_client.assert_called_once()
    mock_es_instance.ping.assert_called_once()
    mock_es_instance.index.assert_not_called()
