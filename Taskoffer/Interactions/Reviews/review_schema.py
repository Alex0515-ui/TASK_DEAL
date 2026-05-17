from pydantic import BaseModel
from typing import Optional



class CreateReviewSchema(BaseModel):
    rating: int 
    comment: Optional[str] = None



