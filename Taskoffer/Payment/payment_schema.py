from pydantic import BaseModel, field_validator

class WalletSchema(BaseModel):
    amount: float 

    @field_validator('amount')
    def validate_price(cls, amount):
        
        if amount <= 0:
            raise ValueError("Цена не может быть отрицательной или 0")
        
        return amount

