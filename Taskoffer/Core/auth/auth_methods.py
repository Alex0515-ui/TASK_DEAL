from pwdlib import PasswordHash
from datetime import datetime, timedelta, timezone
from jose import jwt
from Core.config.configuration import settings
from Core.auth.user_models import User

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

# Метод для хэширования паролей
password_verify = PasswordHash.recommended()


# ======== Хэширование паролей и сравнение их
def hash_password(password: str):
    return password_verify.hash(password)

def verify_password(password:str, hashed_password: str):
    return password_verify.verify(password, hashed_password)
# ================================================================

# Проверка на логин
def authenticate_user(email:str, password:str, db):
    user = db.query(User).filter(User.email==email).first()

    if not user:
        return False
    
    if not verify_password(password=password, hashed_password=user.password_hash):
        return False
    
    return user

# Создание токена
def create_access_token(email:str, user_id:int, expire_time: timedelta):
    encode = {'sub': email, 'id': user_id}
    expires = datetime.now(timezone.utc) + expire_time
    encode.update({'exp': expires})
    return jwt.encode(encode, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM)

# Получение своего профиля
def get_me(user_id: int, db: Session):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Пользователь не найден')
    return {
        "id" : user.id,
        "name" : user.name,
        "email" : user.email,
        "phone_number" : user.phone_number,
        "role" : user.role,
        "rating" : user.rating,
        "completed_tasks" : user.completed_task,
        "registered_at": user.created_at
    }