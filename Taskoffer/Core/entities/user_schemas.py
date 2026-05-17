from pydantic import BaseModel, EmailStr, field_validator, Field
from Core.entities.models import Role
import phonenumbers
from typing import Optional

# Валидация регистрации
class CreateUserSchema(BaseModel):
    name: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password_hash: str = Field(min_length=3, max_length=50)
    phone_number: str
    role: Optional[Role] = Role.CLIENT

    @field_validator('name')
    def validate_name(cls, name):
        if not name.strip():
            raise ValueError("Поле имени не может быть пустым")
        return name
    
    @field_validator('password_hash')
    def validate_password(cls, password):
        if not password.strip():
            raise ValueError("Поле пароля не может быть пустым")
        return password
    
    @field_validator('phone_number')
    def validate_phone_number(cls, number:str):
        try:
            parsed_num = phonenumbers.parse(number)

            if not phonenumbers.is_valid_number(parsed_num):
                raise ValueError("Неправильный формат данных номера телефона")
            
            
            return phonenumbers.format_number(parsed_num, phonenumbers.PhoneNumberFormat.E164)
        except Exception:
            raise ValueError("Номер телефона должен включать код страны: (+7...)")

# Валидация токена в JWT
class Token(BaseModel):
    access_token: str
    token_type: str

# Валидация логина
class LoginSchema(BaseModel):
    email: str
    password: str






        

    
    