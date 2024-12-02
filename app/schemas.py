
from pydantic import BaseModel
from datetime import date

class Child(BaseModel):
    child_id: int
    name: str
    date_of_birth: date
    total_points: int

    class Config:
        orm_mode = True
