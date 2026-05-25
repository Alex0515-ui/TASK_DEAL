from pydantic import BaseModel, Field, field_validator

# Валидация данных для создания сообщения
class CreateMessage(BaseModel):
    text: str = Field(min_length=1, max_length=3000)

    @field_validator("text")
    def validate_text(cls, text):
        if not text.strip():
            raise ValueError("Сообщение не может быть пустым")
        return text
