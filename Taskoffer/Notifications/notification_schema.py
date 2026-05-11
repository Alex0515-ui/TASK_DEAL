from pydantic import BaseModel, Field
from entities.models import NotificationType

class CreateNotification(BaseModel):
    text: str = Field(min_length=5, max_length=500)
    type: NotificationType