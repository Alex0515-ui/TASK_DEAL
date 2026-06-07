from fastapi import APIRouter

from Interactions.Reviews.review_service import ReviewService
from Core.auth.authentication import db_dependency, user_dependency
from Interactions.Reviews.review_schema import CreateReviewSchema



router = APIRouter(prefix="/reviews", tags=["Reviews"])

# Создание отзыва
@router.post("/create/{deal_id}")
def create_review(deal_id: int, data: CreateReviewSchema, user: user_dependency, db: db_dependency):
    return ReviewService.create_review(deal_id=deal_id, data=data, user_id=user['id'], db=db)

# Получение отзывов о себе
@router.get("/got")
def get_all_reviews(user: user_dependency, db: db_dependency, offset: int = 0, limit: int = 10):
    return ReviewService.get_all_his_reviews(user_id=user['id'], db=db, offset=offset, limit=limit)

# Получение своих данных отзывов
@router.get("/my")
def get_my_reviews(user: user_dependency, db: db_dependency, offset: int = 0, limit: int = 10):
    return ReviewService.get_all_made_reviews(user_id=user['id'], db=db, offset=offset, limit=limit)

# Получение отзывов сделки
@router.get("/deal/{deal_id}")
def get_deal_reviews(deal_id: int, user: user_dependency, db: db_dependency):
    return ReviewService.get_deal_reviews(deal_id=deal_id, user_id=user['id'], db=db)

