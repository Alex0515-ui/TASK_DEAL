from pydantic import BaseModel, field_validator, Field

from datetime import datetime
from datetime import datetime, timezone
from Business.Jobs.job_models import Job_type


# Валидация создания работы
class CreateJobSchema(BaseModel):
    title: str = Field(min_length=5, max_length=200)
    description: str = Field(min_length=5, max_length=3000)
    price: int 
    type: Job_type
    expires_at: datetime
    deadline: datetime

    @field_validator('title')
    def validate_title(cls, title):
        if not title.strip():
            raise ValueError("Поле названия работы не может быть пустым")
        
        return title
    
    @field_validator('description')
    def validate_description(cls, desc):
        if not desc.strip():
            raise ValueError("Поле описания не может быть пустым")
        
        return desc
    
    @field_validator('deadline')
    def validate_deadline(cls, deadline):

        if deadline.tzinfo is None:
            deadline = deadline.replace(tzinfo=timezone.utc)

        if deadline < datetime.now(timezone.utc):
            raise ValueError("Дедлайн должен быть в будущем, а не в прошлом!")
        
        return deadline
        
    @field_validator('expires_at')
    def validate_deadline(cls, expire):
        if expire.tzinfo is None:
            expire = expire.replace(tzinfo=timezone.utc)

        if expire < datetime.now(timezone.utc):
            raise ValueError("Срок истечения работы должен быть в будущем, а не в прошлом!")
        else:
            return expire
        
    @field_validator('price')
    def validate_price(cls, price):
        if price <= 0:
            raise ValueError("Цена не может быть отрицательной или 0")
        
        return price
    


    