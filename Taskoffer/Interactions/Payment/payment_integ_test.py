from fastapi.testclient import TestClient
from datetime import timedelta

from main import app
from Core.auth.authentication import create_access_token

client = TestClient(app)

# =======================================================================
# ======================= CHECK BALANCE TESTS ==============================
# ==============================================================================

# Успешная проверка баланса
def test_check_balance_integ_success(client_user, client_wallet):
    token = create_access_token(client_user.email, client_user.id, expire_time=timedelta(minutes=30))

    response = client.get("/wallet/my", headers={"Authorization": f"Bearer {token}"})
    data = response.json()

    assert response.status_code == 200
    assert data['balance'] == 20000

# Ошибка авторизации
def test_check_balance_integ_fail():

    response = client.get("/wallet/my", headers={"Authorization": f"Bearer qwdjlwqjdqwd"})

    assert response.status_code == 401

# ======================================================================
# ================= REFILL WALLET TESTS ==========================
# =======================================================================

# Успешная проверка баланса
def test_refill_integ_success(client_user, client_wallet):
    token = create_access_token(client_user.email, client_user.id, expire_time=timedelta(minutes=30))

    response = client.patch("/wallet/fill", 
    headers={"Authorization": f"Bearer {token}"},
    json = {
        "amount": 10000
    }
    )

    data = response.json()

    assert response.status_code == 200
    assert data['status'] == 'success'
    assert data['balance'] == 30000

# Ошибка авторизации
def test_refill_integ_fail():

    response = client.patch("/wallet/fill", headers={"Authorization": f"Bearer qwdjlwqjdqwd"}, json={"amount": 10000})

    assert response.status_code == 401

# ====================================================================================
# =================== WITHDRAW WALLET TESTS =======================================
# ===========================================================================================

# Успешная проверка баланса
def test_withdraw_integ_success(client_user, client_wallet):
    token = create_access_token(client_user.email, client_user.id, expire_time=timedelta(minutes=30))

    response = client.patch("/wallet/withdraw", 
    headers={"Authorization": f"Bearer {token}"},
    json = {
        "amount": 10000
    }
    )

    data = response.json()

    assert response.status_code == 200
    assert data['status'] == 'success'
    assert data['balance'] == 10000

# Ошибка авторизации
def test_withdraw_integ_fail():

    response = client.patch("/wallet/withdraw", headers={"Authorization": f"Bearer qwdjlwqjdqwd"}, json={"amount": 10000})

    assert response.status_code == 401