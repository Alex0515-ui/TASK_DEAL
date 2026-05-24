import pytest
from fastapi.testclient import TestClient
from datetime import timedelta

from main import app
from Core.auth.authentication import create_access_token
from Core.entities.models import *

client = TestClient(app)


# ========================================================================
# ====================== REGISTER TESTS ========================================
# =========================================================================================
# Успешная регистрация как клиент
@pytest.mark.asyncio
async def test_register_integ_user_success(db, client_user):

    response = client.post("/auth/register", json={
        "name":"Test user", 
        "email":"test@gmail.com", 
        "password_hash":"12345", 
        "phone_number":"+77472894467", 
        "role":Role.CLIENT.value
    })
    data = response.json()

    assert response.status_code == 201
    assert data['message'] == "Пользователь создался успешно!"


# Успешная регистрация как работник
@pytest.mark.asyncio
async def test_register_integ_worker_success(db, client_user):

    response = client.post("/auth/register", json={
        "name":"Test user", 
        "email":"test@gmail.com", 
        "password_hash":"12345", 
        "phone_number":"+77472894667", 
        "role":Role.WORKER.value
    })
    data = response.json()

    assert response.status_code == 201
    assert data['message'] == "Пользователь создался успешно!"


# Ошибка что такой email уже есть
@pytest.mark.asyncio
async def test_register_integ_email_fail(db, client_user):

    response = client.post("/auth/register", json={
        "name":"Test user", 
        "email":client_user.email,  
        "password_hash":"12345", 
        "phone_number":"+77472894547", 
        "role":Role.CLIENT.value
    })

    assert response.status_code == 400


# Ошибка что такой номер телефона уже есть
@pytest.mark.asyncio
async def test_register_integ_number_fail(db, client_user):

    response = client.post("/auth/register", json={
        "name":"Test user", 
        "email":"Test@gmail.com",   
        "password_hash":"12345", 
        "phone_number":client_user.phone_number, 
        "role":Role.CLIENT.value
    })

    assert response.status_code == 400

# =======================================================================================
# ======================= LOGIN TESTS ==============================================
# =================================================================================

# Успешный логин
@pytest.mark.asyncio
async def test_login_success(client_user):

    response = client.post("/auth/token", json={
        "email": client_user.email,
        "password": "123"
    })
    data = response.json()
    assert response.status_code == 200
    assert data['token_type'] == "bearer" 


# Ошибка что такой пользователь не существует
@pytest.mark.asyncio
async def test_login_fail(client_user):

    response = client.post("/auth/token", json={
        "email": "Blasndwewmdd@gmail.com",
        "password": "123"
    })

    assert response.status_code == 401

# ===========================================================================
# ================== GET_ME TESTS =====================================
# =========================================================================

# Успешное получение своего профиля
def test_get_me_success(client_user):
    token = create_access_token(email=client_user.email, user_id=client_user.id, expire_time=timedelta(minutes=30))
    
    response = client.get("/auth/me", headers={
        "Authorization": f"Bearer {token}"
    })
    data = response.json()

    assert response.status_code == 200
    assert data['id'] == client_user.id
    assert data['email'] == client_user.email


# Ошибка авторизации
def test_get_me_fail():
    
    response = client.get("/auth/me", headers={
        "Authorization": f"Bearer qwddqwdqwdqwd"
    })

    assert response.status_code == 401





    






