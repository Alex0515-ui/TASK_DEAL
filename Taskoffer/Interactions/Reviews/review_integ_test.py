from fastapi.testclient import TestClient
from datetime import timedelta

from main import app
from Core.auth.authentication import create_access_token
from Core.entities.models import *

client = TestClient(app)

# ===================================================================================
# =============== CREATE REVIEW TESTS ===================================================
# =================================================================================

# Успешное создание отзыва
def test_create_review_integ_success(db, client_user, deal):
    token = create_access_token(client_user.email, client_user.id, expire_time=timedelta(minutes=30))

    deal.status = DealStatus.COMPLETED
    db.commit()

    response = client.post(f"/reviews/create/{deal.id}", headers={"Authorization": f"Bearer {token}"}, json={
        "rating": 5,
        "comment": "Just a test"
    })
    data = response.json()

    assert response.status_code == 200
    assert data['from_user_id'] == client_user.id 

# Ошибка авторизации
def test_create_review_integ_fail(db, client_user, deal):

    deal.status = DealStatus.COMPLETED
    db.commit()

    response = client.post(f"/reviews/create/{deal.id}", headers={"Authorization": f"Bearer qwkjhdwjwd"}, json={
        "rating": 5,
        "comment": "Just a test"
    })

    assert response.status_code == 401

# ===========================================================================
# ================ GET_ALL_REVIEWS TESTS ======================================
# =============================================================================

# Получение всех отзывов о себе
def test_get_all_reviews_integ_success(db, client_user):
    token = create_access_token(client_user.email, client_user.id, expire_time=timedelta(minutes=30))

    response = client.get("/reviews/got", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200

# Ошибка авторизации
def test_get_all_reviews_integ_fail():

    response = client.get("/reviews/got", headers={"Authorization": f"Bearer qwkjhdwjwd"})

    assert response.status_code == 401


# ====================================================================
# =========== GET_MY_REVIEWS TESTS ===================================
# ==========================================================================

# Получение всех поставленных отзывов
def test_get_my_reviews_integ_success(db, client_user):
    token = create_access_token(client_user.email, client_user.id, expire_time=timedelta(minutes=30))

    response = client.get("/reviews/my", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200

# Ошибка авторизации
def test_get_my_reviews_integ_fail():

    response = client.get("/reviews/my", headers={"Authorization": f"Bearer qwkjhdwjwd"})

    assert response.status_code == 401


