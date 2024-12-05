# create activity model
from typing import Optional
from pydantic import BaseModel
from sqlalchemy import DateTime, Integer, String, Text


class ActivityCreate (BaseModel):
    branch_id :Integer
    name :String
    description :Text
    location :String
    start_time :DateTime
    end_time :DateTime
    points_awarded :Integer

    class Config:
       orm_mode = True    
       arbitrary_types_allowed = True

class ActivityEdit(BaseModel):
    branch_id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    start_time: Optional[DateTime] = None
    end_time: Optional[DateTime] = None
    points_awarded: Optional[int] = None

    class Config:
        orm_mode = True    
        arbitrary_types_allowed = True

class LoginRequest(BaseModel):
    user_name: str
    password: str