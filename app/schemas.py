from pydantic import BaseModel
from typing import Optional

class UserInput(BaseModel):
    username: str
    user_id: int
    age: int
    weight: float
    goal: str
    intensity: str

class FeedbackRequest(BaseModel):
    user_id: int
    feedback: str
