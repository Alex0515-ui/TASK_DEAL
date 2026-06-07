from pydantic import BaseModel, field_validator
from typing import Optional

# Валидация создания заявки на работу
class CreateJobResponseSchema(BaseModel):
    job_id: int
    offered_price: Optional[int] = None
    cover_letter: Optional[str] = None


    @field_validator('offered_price')
    def validate_price(cls, price):
        if price is None:
            return price
        
        if price <= 0:
            raise ValueError("Цена не может быть отрицательной или 0")
        
        return price
    
    @field_validator('cover_letter')
    def validate_message(cls, message):
        if message is None:
            return message
        
        if not message.strip():
            raise ValueError("Сообщение не может быть пустым")
        
        return message
    

class DeleteJobResponseSchema(BaseModel):
    job_id: int

    @field_validator('job_id')
    def validate_id(cls, job_id):
        if job_id < 1:
            return ValueError("ID не может быть меньше 1")
        return job_id
    