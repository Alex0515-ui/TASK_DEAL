from fastapi.testclient import TestClient
from datetime import datetime, timedelta, timezone
from main import app
from Core.auth.auth_methods import create_access_token
from Business.Deals.deal_models import DealStatus


client = TestClient(app)

# ======================================================================
# =================== CHANGE_DEAL TESTS ==============================
# ==========================================================================


# Успешное изменение сделки
def test_change_deal_integ_success(db, client_user, deal):
    token = create_access_token(email=client_user.email, user_id=client_user.id, expire_time=timedelta(minutes=30))

    response_api = client.put(
        f"/deals/change/{deal.id}", 
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
        "agreed_price": 10000,
        "reason": "Just a test"
    })

    assert response_api.status_code == 200

    data = response_api.json()
    assert data['message'] == "Сделка успешно обновлена! Подпишите ее с обеих сторон!"

# Не авторизованный пользователь
def test_change_deal_integ_fail(deal):

    response_api = client.put(
        f"/deals/change/{deal.id}", 
        headers={
            "Authorization": f"Bearer qwdqwdwqddw"
        },
        json={
        "agreed_price": 10000,
        "reason": "Just a test"
    })

    assert response_api.status_code == 401


# ==============================================================================
# ================== GET DEAL TESTS =================================
# ================================================================================

# Успешное получение сделки
def test_get_deal_integ_success(db, client_user, deal):
    token = create_access_token(email=client_user.email, user_id=client_user.id, expire_time=timedelta(minutes=30))

    response_api = client.get(
        f"/deals/get/{deal.id}", 
        headers={
            "Authorization": f"Bearer {token}"
        })

    assert response_api.status_code == 200

    data = response_api.json()
    assert data['client_id'] == client_user.id

# Ошибка с авторизацией
def test_get_deal_integ_fail(db, client_user, deal):

    response_api = client.get(
        f"/deals/get/{deal.id}", 
        headers={
            "Authorization": f"Bearer qwdqdwdqwdwdwq"
        })

    assert response_api.status_code == 401

# ==================================================================================
# ======================= SIGN DEAL TESTS =====================================
# ===================================================================================

# Успешная подпись сделки
def test_sign_deal_integ_success(db, client_user, deal):
    token = create_access_token(email=client_user.email, user_id=client_user.id, expire_time=timedelta(minutes=30))
    
    deal.status = DealStatus.NEGOTIATION
    db.commit()

    response_api = client.patch(
        f"/deals/sign/{deal.id}", 
        headers={
            "Authorization": f"Bearer {token}"
        })

    assert response_api.status_code == 200

    data = response_api.json()

# Ошибка с авторизацией 
def test_sign_deal_integ_fail(db, client_user, deal):
    
    deal.status = DealStatus.NEGOTIATION
    db.commit()

    response_api = client.patch(
        f"/deals/sign/{deal.id}", 
        headers={
            "Authorization": f"Bearer qswdwddwddw"
        })

    assert response_api.status_code == 401

# ========================================================================
# ========================= COMPLETE DEAL TESTS ======================
# =============================================================================

# Успешное завершение сделки
def test_complete_deal_integ_success(db, client_user, deal, worker_wallet):
    token = create_access_token(email=client_user.email, user_id=client_user.id, expire_time=timedelta(minutes=30))
    
    deal.status = DealStatus.ACTIVE
    deal.worker_completed_at = datetime.now(timezone.utc)
    db.commit()

    response_api = client.patch(
        f"/deals/complete/{deal.id}", 
        headers={
            "Authorization": f"Bearer {token}"
        })

    assert response_api.status_code == 200

    data = response_api.json()
    assert data['message'] == "Сделка успешно завершена с обеих сторон!"

# Ошибка авторизации
def test_complete_deal_integ_fail(db, deal):
    
    deal.status = DealStatus.ACTIVE
    db.commit()

    response_api = client.patch(
        f"/deals/complete/{deal.id}", 
        headers={
            "Authorization": f"Bearer wdwqqwdqwqwdqd"
        })

    assert response_api.status_code == 401


# Успешная отмена сделки
def test_cancel_deal_integ_success(db, client_user, deal, client_wallet):
    token = create_access_token(email=client_user.email, user_id=client_user.id, expire_time=timedelta(minutes=30))
    
    deal.status = DealStatus.ACTIVE
    db.commit()

    response_api = client.patch(
        f"/deals/cancel/{deal.id}", 
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "reason": "Just a test"
        })

    assert response_api.status_code == 200

    data = response_api.json()
    assert data['message'] == "Сделка отменена"

# Ошибка авторизации
def test_cancel_deal_integ_fail(db, deal):
    
    deal.status = DealStatus.ACTIVE
    db.commit()

    response_api = client.patch(
        f"/deals/cancel/{deal.id}",
        json={
            "reason": "Just a test"
        }, 
        headers={
            "Authorization": f"Bearer wdwqqwdqwqwdqd"
        }
        )
    

    assert response_api.status_code == 401






