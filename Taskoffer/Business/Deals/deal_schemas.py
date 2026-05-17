from pydantic import BaseModel, field_validator, Field, model_validator
from datetime import datetime
from typing import Optional
from datetime import datetime, timezone


class CancelDealSchema(BaseModel):
    reason: str = Field(min_length=5, max_length=1000)

    @field_validator('reason')
    def validate_reason(cls, reason):
        if not reason.strip():
            raise ValueError("Поле причины не может быть пустым")
        
        return reason

class ChangeDealSchema(BaseModel):
    agreed_price: Optional[int] = None
    deadline: Optional[datetime] = None
    reason: str = Field(min_length=5, max_length=1000)

        
    @field_validator('deadline')
    def validate_deadline(cls, deadline):
        if deadline is None:
            return deadline
        
        if deadline.tzinfo is None:
            deadline = deadline.replace(tzinfo=timezone.utc)

        if deadline < datetime.now(timezone.utc):
            raise ValueError("Дедлайн должен быть в будущем, а не в прошлом!")
        
        return deadline
        
    @field_validator('agreed_price')
    def validate_price(cls, price):
        if price is None:
            return price
        
        if price <= 0:
            raise ValueError("Цена не может быть отрицательной или 0")
        
        return price
        
    @field_validator('reason')
    def validate_reason(cls, reason):
        if not reason.strip():
            raise ValueError("Поле причины не может быть пустым")
        
        return reason
        
    @model_validator(mode="after")
    def check_fields_not_empty(self):
        if self.agreed_price is None and self.deadline is None:
            raise ValueError("Нужно изменить цену либо сроки выполнения")
        
        return self