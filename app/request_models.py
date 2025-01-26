# create activity model
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from sqlalchemy import DateTime, Integer, String, Text

from app import db_models, response_models


class ActivityCreate (BaseModel):
    name :String
    description :Text
    location :String
    start_time :DateTime
    end_time :DateTime

    class Config:
       orm_mode = True    
       arbitrary_types_allowed = True

class ActivityEdit(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    start_time: Optional[DateTime] = None
    end_time: Optional[DateTime] = None

    class Config:
        orm_mode = True    
        arbitrary_types_allowed = True

class LoginRequest(BaseModel):
    user_name: str
    password: str


class messageRequest(BaseModel):
    message: str
    user_ids: int  # List of user IDs to send the message to
    sent_by: int  # ID of the user sending the message
    reply_to_notification_id: Optional[int] = None  # שדה אופציונלי להודעה קודמת
    forward_reason:Optional[str]=None
    class Config:
        orm_mode = True    
        arbitrary_types_allowed = True
class messagesRequest(BaseModel):
    message: str
    user_ids: List[int]  # List of user IDs to send the message to
    sent_by: int  # ID of the user sending the message
    reply_to_notification_id: Optional[int] = None  # שדה אופציונלי להודעה קודמת
    forward_reason:Optional[str]=None
    class Config:
        orm_mode = True    
        arbitrary_types_allowed = True
class RegisterRequest(BaseModel):
    user_name: str
    email: EmailStr
    password: str
    role_id: int

    class Config:
        orm_mode = True
class BranchCreate(BaseModel):
    branch_name: str
    location: str
    class Config:
        orm_mode = True
class ActivityCreate(BaseModel):
    name: str
    description: Optional[str]
    location: Optional[str]
    start_time: datetime
    end_time: datetime


class ActivityEdit(BaseModel):
    name: Optional[str]
    description: Optional[str]
    location: Optional[str]
    start_time: Optional[datetime]
    end_time: Optional[datetime]
class LoginUserCreate(BaseModel):
    user_name: str
    email: EmailStr
    phone: str
    password: str
class BranchManagerCreate(BaseModel):
    branch_id: int

class BranchManagerCreate(BaseModel):
    login_user: LoginUserCreate
    branch_manager:BranchManagerCreate
    class Config:
        arbitrary_types_allowed = True

class BranchManagerUpdate(BaseModel):
    login_user: response_models.LoginUser
    branch_manager: response_models.BranchManager
class BranchGroupCreate(BaseModel):
    group_name: str 
class ParentIdRequest(BaseModel):
    parent_id: int