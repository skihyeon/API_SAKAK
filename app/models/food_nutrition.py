from sqlalchemy import Column, Integer, String, Float
from app.db.session import Base 

class FoodNutrition(Base):
    __tablename__ = "food_nutritions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)          ## 1. 번호
    food_cd = Column(String(50), unique=True, index=True, nullable=False)           ## 2. 식품코드
    group_name = Column(String(100))                                                ## 3. 식품군
    food_name = Column(String(255), index=True, nullable=False)                     ## 4. 식품이름
    research_year = Column(String(4), index=True)                                   ## 5. 조사년도
    maker_name = Column(String(100), index=True)                                    ## 6. 지역/제조사
    ref_name = Column(String(255))                                                  ## 7. 자료출처
    serving_size = Column(Float)                                                    ## 8. 1회 제공량
    calorie = Column(Float)                                                         ## 9. 열량(kcal)(1회제공량당)
    carbohydrate = Column(Float)                                                    ## 10. 탄수화물(g)(1회제공량당)
    protein = Column(Float)                                                         ## 11. 단백질(g)(1회제공량당)
    province = Column(Float)                                                        ## 12. 지방(g)(1회제공량당)
    sugars = Column(Float)                                                          ## 13. 총당류(g)(1회제공량당)
    salt = Column(Float)                                                            ## 14. 나트륨(mg)(1회제공량당)
    cholesterol = Column(Float)                                                     ## 15. 콜레스테롤(mg)(1회제공량당)
    saturated_fatty_acids = Column(Float)                                           ## 16. 포화지방산(g)(1회제공량당)
    trans_fat = Column(Float)                                                       ## 17. 트랜스지방(g)(1회제공량당)

    def __repr__(self):
        return f"<FoodNutrition(id={self.id}, food_name='{self.food_name}', food_cd='{self.food_cd}')>"