from fastapi.testclient import TestClient
from datetime import timedelta

from main import app
from Core.auth.authentication import create_access_token
from Core.entities.models import *

client = TestClient(app)

# ===============================================================
# =================== CREATE MESSAGE TESTS ============================
# ==========================================================================

# Успешная отправка сообщения
def test_create_message_integ_success(client_user, deal):
    token = create_access_token(email=client_user.email, user_id=client_user.id, expire_time=timedelta(minutes=30))

    response = client.post(f"/messages/{deal.id}/create", headers={
        "Authorization": f"Bearer {token}"
    },
    json={
        "text":"Test hello"
    })
    data = response.json()

    assert response.status_code == 200
    assert data['sender_id'] == client_user.id


# Ошибка авторизации
def test_create_message_integ_fail(client_user, deal):

    response = client.post(f"/messages/{deal.id}/create", headers={
        "Authorization": f"Bearer qwwddqwddq"
    },
    json={
        "text":"Test hello"
    })
    data = response.json()

    assert response.status_code == 401

# ==========================================================
# ====================== GET CHAT MESSAGES TESTS ======================
# =======================================================================


# Успешное получение сообщений 
def test_get_messages_integ_success(client_user, deal):
    token = create_access_token(email=client_user.email, user_id=client_user.id, expire_time=timedelta(minutes=30))

    response = client.get(f"/messages/{deal.id}/all", headers={
        "Authorization": f"Bearer {token}"
    })

    assert response.status_code == 200


# Ошибка авторизации
def test_get_messages_integ_fail(deal):

    response = client.get(f"/messages/{deal.id}/all", headers={
        "Authorization": f"Bearer qwwddqwddq"
    })
    data = response.json()

    assert response.status_code == 401


# ===============================================================================
# ================================= MARK AS READ TESTS ===============================
# ====================================================================================

# Успешная маркировка
def test_mark_message_integ_success(client_user, deal):
    token = create_access_token(email=client_user.email, user_id=client_user.id, expire_time=timedelta(minutes=30))

    response = client.patch(f"/messages/{deal.id}/mark", headers={
        "Authorization": f"Bearer {token}"
    })

    assert response.status_code == 200


# Ошибка авторизации
def test_mark_message_integ_fail(deal):

    response = client.patch(f"/messages/{deal.id}/mark", headers={
        "Authorization": f"Bearer qwwddqwddq"
    })

    assert response.status_code == 401