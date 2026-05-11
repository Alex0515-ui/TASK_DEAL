from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from Reviews.review_schema import CreateReviewSchema
from entities.models import *
from datetime import datetime, timezone, timedelta
from Notifications.notification_service import create_notification

class ReviewService:

    # Изменение рейтинга пользователя (Для локальных вызовов сделал)
    @staticmethod
    def rate_user(to_user_id: int, db: Session):

        user = db.query(User).filter(User.id == to_user_id).first()

        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Пользователь не найден')

        reviews = db.query(Review).filter(Review.to_user_id == to_user_id).all()

        if reviews:
            user.rating = sum(r.rating for r in reviews)/len(reviews)
            user.completed_task = len(reviews)

        else:
            user.rating = 5.0
            user.completed_task = 0

        return user


    # Получить все отзывы
    @staticmethod
    def get_all_his_reviews(user_id: int, db: Session, offset: int = 0, limit: int = 10):
        reviews = db.query(Review).filter(Review.to_user_id == user_id)

        return reviews.order_by(Review.created_at.desc()).offset(offset).limit(limit).all()
    
    
    # Получить все поставленные отзывы
    @staticmethod
    def get_all_made_reviews(user_id: int, db: Session, offset: int = 0, limit: int = 10):
        reviews = db.query(Review).filter(Review.from_user_id == user_id)

        return reviews.order_by(Review.created_at.desc()).offset(offset).limit(limit).all()
    
    
    # Получить отзывы сделки
    @staticmethod
    def get_deal_reviews(deal_id: int, user_id: int, db: Session):
        deal = db.query(Deal).filter(Deal.id == deal_id).first()
        if not deal:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Сделка не найдена')
        
        if user_id not in [deal.client_id, deal.worker_id]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Нельзя смотреть отзыв чужой сделки')
        
        reviews = db.query(Review).filter(Review.deal_id == deal_id).all()

        return reviews
    

    # Создание отзыва
    @staticmethod
    def create_review(deal_id: int, data: CreateReviewSchema, user_id: int, db: Session):
        deal = db.query(Deal).filter(Deal.id == deal_id).first()

        if not deal:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Сделка не найдена')
        
        if deal.status != DealStatus.COMPLETED:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Сделка еще не завершена')
        
        if user_id == deal.client_id:
            to_user_id = deal.worker_id

        elif user_id == deal.worker_id:
            to_user_id = deal.client_id


        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail = 'Нельзя ставить оценку чужой сделке')
        
        now = datetime.now(timezone.utc)

        existing = db.query(Review).filter(Review.deal_id == deal_id, Review.from_user_id == user_id).first()
        if existing:

            expire = now - existing.created_at
            if expire > timedelta(days=7):            # Нельзя после 7 дней изменить отзыв
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Время изменения отзыва истекло')
            
            existing.rating = data.rating
            existing.comment = data.comment

            create_notification(
                user_id=to_user_id,
                text=f"Был изменен отзыв о вас по работе '{deal.job.title}'",
                type=NotificationType.JOB,
                db=db,
                related_id=existing.id
            )

            ReviewService.rate_user(to_user_id=to_user_id, db=db)


            db.commit()
            db.refresh(existing)

            
            return existing
        
        review = Review(
            deal_id = deal_id, 
            from_user_id = user_id, 
            to_user_id = to_user_id, 
            rating = data.rating, 
            comment = data.comment
        )
        
        db.add(review)
        db.flush()   # Чтобы изменения уходили в БД без коммита даже

        create_notification(
            user_id=to_user_id,
            text=f"Вы получили отзыв по работе '{deal.job.title}'",
            type=NotificationType.JOB,
            db=db,
            related_id=review.id
        )

        ReviewService.rate_user(to_user_id=to_user_id, db=db)
        
        db.commit()
        
        return review
    



        