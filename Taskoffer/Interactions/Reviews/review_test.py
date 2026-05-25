import pytest
from pytest_mock import mocker
from fastapi import HTTPException

from Interactions.Reviews.review_service import ReviewService
from Interactions.Reviews.review_schema import CreateReviewSchema
from Core.entities.models import *
from datetime import datetime, timezone, timedelta


# Успешная оценка работника
def test_rate_user_success(deal, client_user, worker_user, db):

    expire = datetime.now(timezone.utc) - timedelta(days=9)
    deadline = datetime.now(timezone.utc) - timedelta(days=3)


    job = Job(
        title="Test job", 
        description="Test desc job", 
        price=10000, 
        type=Job_type.REPAIR, 
        status=Job_status.DONE,
        expires_at=expire, 
        deadline = deadline,
        owner_id = client_user.id,
        worker_id = worker_user.id
    )
    job2 = Job(
        title="Test job", 
        description="Test desc job", 
        price=10000, 
        type=Job_type.REPAIR, 
        status=Job_status.DONE,
        expires_at=expire - timedelta(hours=12), 
        deadline = deadline - timedelta(days=1),
        owner_id = client_user.id,
        worker_id = worker_user.id
    )

    db.add_all([job, job2])
    db.flush()

    deal1 = Deal(
        job_id = job.id,
        worker_id = worker_user.id,
        client_id = client_user.id,
        worker_email=worker_user.email, 
        client_email=client_user.email, 
        deadline=job.deadline,
        agreed_price=10000,
        status=DealStatus.COMPLETED,
        worker_phone_number=worker_user.phone_number, 
        client_phone_number=client_user.phone_number
    )

    deal2 = Deal(
        job_id = job2.id,
        worker_id = worker_user.id,
        client_id = client_user.id,
        worker_email=worker_user.email, 
        client_email=client_user.email, 
        agreed_price=10000,
        status=DealStatus.COMPLETED,
        deadline=job.deadline - timedelta(days=1),
        worker_phone_number=worker_user.phone_number, 
        client_phone_number=client_user.phone_number
    )
    
    db.add_all([deal1, deal2])
    db.flush()

    review = Review(deal_id=deal1.id, from_user_id=client_user.id, to_user_id=worker_user.id, rating=4.0)
    review2 = Review(deal_id=deal2.id, from_user_id=client_user.id, to_user_id=worker_user.id, rating=2.0)

    db.add_all([review, review2])
    db.commit()

    result = ReviewService.rate_user(to_user_id=worker_user.id, db=db)

    assert result.rating == 3.0

# Оценка работника у которого еще не было оценок
def test_rate_user_without_grades_success(deal, client_user, worker_user, db):

    data = CreateReviewSchema(rating=3.0, comment="Just a test")

    result = ReviewService.rate_user(to_user_id=worker_user.id, db=db)

    assert result.rating == 5.0

# Ошибка что пользователь не найден
def test_rate_user_not_found_fail(db):

    with pytest.raises(HTTPException) as exc:
        ReviewService.rate_user(to_user_id=99999, db=db)

    assert exc.value.status_code == 404


# ==============================================================================================
# ====================== CREATE_REVIEW TESTS =======================================
# ================================================================================================

# Успешное создание отзыва
def test_create_review_success(mocker, db, worker_user, client_user, deal):
    notification = mocker.patch("Interactions.Reviews.review_service.create_notification")
    rating_func = mocker.patch("Interactions.Reviews.review_service.ReviewService.rate_user")

    data = CreateReviewSchema(rating=4.0, comment="Just a test")

    deal.status = DealStatus.COMPLETED
    db.commit()

    result = ReviewService.create_review(deal_id=deal.id, data=data, user_id=client_user.id, db=db)

    assert result is not None
    notification.assert_called_once()
    rating_func.assert_called_once()

# Успешное изменение отзыва
def test_create_review_change_success(mocker, db, worker_user, client_user, deal):
    notification = mocker.patch("Interactions.Reviews.review_service.create_notification")
    rating_func = mocker.patch("Interactions.Reviews.review_service.ReviewService.rate_user")

    data = CreateReviewSchema(rating=4.0, comment="Just a test")
    rated_at = datetime.now(timezone.utc) - timedelta(days=2)

    review = Review(
        deal_id=deal.id, 
        from_user_id=client_user.id, 
        to_user_id=worker_user.id, 
        rating=3.0, 
        created_at = rated_at
    )

    deal.status = DealStatus.COMPLETED
    db.add(review)
    db.commit()

    result = ReviewService.create_review(deal_id=deal.id, data=data, user_id=client_user.id, db=db)

    assert result is not None
    assert result.rating == 4.0
    notification.assert_called_once()
    rating_func.assert_called_once()

# Ошибка что сделка не найдена
def test_create_review_deal_not_found_fail(mocker, db, worker_user, client_user, deal):
    notification = mocker.patch("Interactions.Reviews.rreview_service.create_notification")
    rating_func = mocker.patch("Interactions.Reviews.review_service.ReviewService.rate_user")

    data = CreateReviewSchema(rating=4.0, comment="Just a test")

    deal.status = DealStatus.COMPLETED
    db.commit()

    with pytest.raises(HTTPException) as exc:
        ReviewService.create_review(deal_id=99999, data=data, user_id=client_user.id, db=db)

    assert exc.value.status_code == 404
    notification.assert_not_called()
    rating_func.assert_not_called()


# Ошибка что сделка не завершена
def test_create_review_deal_not_completed_fail(mocker, db, worker_user, client_user, deal):
    notification = mocker.patch("Interactions.Reviews.review_service.create_notification")
    rating_func = mocker.patch("Interactions.Reviews.review_service.ReviewService.rate_user")

    data = CreateReviewSchema(rating=4.0, comment="Just a test")

    with pytest.raises(HTTPException) as exc:
        ReviewService.create_review(deal_id=deal.id, data=data, user_id=client_user.id, db=db)

    assert exc.value.status_code == 400
    notification.assert_not_called()
    rating_func.assert_not_called()


# Ошибка что нельзя изменить отзыв после 7 дней 
def test_create_review_change_expire_fail(mocker, db, worker_user, client_user, deal):
    notification = mocker.patch("Interactions.Reviews.review_service.create_notification")
    rating_func = mocker.patch("Interactions.Reviews.review_service.ReviewService.rate_user")

    data = CreateReviewSchema(rating=4.0, comment="Just a test")

    rated_at = datetime.now(timezone.utc) - timedelta(days=8)

    review = Review(
        deal_id=deal.id, 
        from_user_id=client_user.id, 
        to_user_id=worker_user.id, 
        rating=3.0, 
        created_at = rated_at
    )

    deal.status = DealStatus.COMPLETED
    db.add(review)
    db.commit()

    with pytest.raises(HTTPException) as exc:
        ReviewService.create_review(deal_id=deal.id, data=data, user_id=client_user.id, db=db)

    assert exc.value.status_code == 400
    notification.assert_not_called()
    rating_func.assert_not_called()



