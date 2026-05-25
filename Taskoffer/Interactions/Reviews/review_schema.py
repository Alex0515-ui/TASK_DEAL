from pydantic import BaseModel, field_validator
from typing import Optional

# Простая валидация отзыва
class CreateReviewSchema(BaseModel):
    rating: int 
    comment: Optional[str] = None

    @field_validator('rating')
    def validate_rating(cls, rating):
        if rating < 0:
            raise ValueError("Рейтинг не может быть ниже нуля")
        return rating
    
    @field_validator('comment')
    def validate_comment(cls, comment):
        if len(comment.strip()) < 3:
            raise ValueError("Нельзя отправить такой короткий комментарий")
        return comment



