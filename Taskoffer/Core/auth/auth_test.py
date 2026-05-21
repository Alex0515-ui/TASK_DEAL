import pytest
from pytest_mock import mocker
from fastapi import HTTPException
from Core.auth.auth_methods import *
from Core.auth.authentication import *
from Core.config.configuration import settings


# =======================================================================
# ================ AUTHENTICATE USER TESTS ===============================
# =============================================================================

# Успешная аутентификация
def test_authenticate_user_success(client_user, db, mocker):
    verified = mocker.patch("Core.auth.auth_methods.verify_password")

    result = authenticate_user(email=client_user.email, password="123", db=db)

    assert result.email == client_user.email
    assert result.password_hash == client_user.password_hash
    verified.assert_called_once()

# Ошибка что пользователь не найден
def test_authenticate_user_not_found_fail(client_user, db, mocker):
    verified = mocker.patch("Core.auth.auth_methods.verify_password")

    result = authenticate_user(email="blablabla", password="123", db=db)

    assert result is False
    verified.assert_not_called()


# Ошибка что пароль не совпал
def test_authenticate_user_password_incorrect_fail(client_user, db, mocker):
    verified = mocker.patch("Core.auth.auth_methods.verify_password", return_value=False)

    result = authenticate_user(email=client_user.email, password="12345", db=db)

    assert result is False
    verified.assert_called_once()


# ========================================================================
# ===================== CREATE ACCESS TOKEN TESTS ======================
# =========================================================================

# Успешное создание токена
def test_create_token_success(client_user):
    
    result = create_access_token(email=client_user.email, user_id=client_user.id, expire_time=timedelta(minutes=30))

    payload = jwt.decode(result, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])

    assert payload['sub'] == client_user.email
    assert payload['id'] == client_user.id


# ======================================================================================
# ================================ GET_CURRENT_USER TESTS ===============================
# ==========================================================================================

# Успешное получение пользователя для авторизации
@pytest.mark.asyncio
async def test_get_current_user_success(client_user):

    token = create_access_token(email=client_user.email, user_id=client_user.id, expire_time=timedelta(minutes=30))

    result = await get_current_user(token=token)

    assert result['email'] == client_user.email
    assert result['id'] == client_user.id

# Ошибка что поля одного нету в токене
@pytest.mark.asyncio
async def test_get_current_user_missing_field_fail(client_user):

    token = create_access_token(email=client_user.email, user_id=client_user.id, expire_time=timedelta(minutes=30))

    payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])

    payload['sub'] = None 

    incorrect_token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM)

    with pytest.raises(HTTPException) as exc:
        await get_current_user(token=incorrect_token)

    assert exc.value.status_code == 401
    




