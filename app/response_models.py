from pydantic import BaseModel, EmailStr, root_validator
from datetime import date, datetime
from typing import Optional, List

from sqlalchemy import LargeBinary


# Role Model
class Role(BaseModel):
    role_id: int
    role_name: str

    class Config:
        orm_mode = True


# Branch Model
class Branch(BaseModel):
    branch_id: int
    branch_name: str
    location: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True

class BranchGroup(BaseModel):

    group_id:int
    group_name :str
    branch_id :int
    class Config:
        orm_mode = True





# Login User Model
class LoginUser(BaseModel):
    login_user_id: int
    user_name: str
    email: EmailStr
    role_id: int
    chat_id: Optional[str] = None  # מאפשר ערך None
    created_at: datetime
    phone: Optional[str] = None
    class Config:
        orm_mode = True
        from_attributes = True  # נדרש כדי להשתמש ב-from_orm



# Parent Model
class Parent(BaseModel):
    parent_id: int
    login_user_id: int
    additional_info: Optional[str]

    class Config:
        orm_mode = True


# Branch Manager Model
class BranchManager(BaseModel):
    branch_manager_id: int
    login_user_id: int
    branch_id: int
    additional_info: Optional[str]

    class Config:
        orm_mode = True
        from_attributes = True  # נדרש כדי להשתמש ב-from_orm


# Secretary Model
class Secretary(BaseModel):
    secretary_id: int
    login_user_id: int
    additional_info: Optional[str]

    class Config:
        orm_mode = True


# Child Model
class Child(BaseModel):
    child_id: int
    parent_id: int
    branch_group_id: Optional[int]
    first_name: str
    date_of_birth: date
    id_number: Optional[str] = None
    school_name: Optional[str] = None
    street: Optional[str] = None
    house_number: Optional[str] = None
    city: Optional[str] = None
    parent_email: Optional[str] = None
    mother_name: Optional[str] = None
    mother_phone: Optional[str] = None
    father_name: Optional[str] = None
    father_phone: Optional[str] = None
    branch_id: Optional[int] = None
    class_id: Optional[int] = None
    shirt_size_id: Optional[int] = None
    total_points: int
    branch_manager_id:Optional[int]=None
    last_name: Optional[str] = None
    nickname: Optional[str] = None
    phone: Optional[str] = None
    image: Optional[bytes]=None
   
    class Config:
        orm_mode = True



# Activity Model
class Activity(BaseModel):
    activity_id: int
    name: str
    description: Optional[str]
    location: Optional[str]
    start_time: datetime
    end_time: datetime
    points_limit: int

    class Config:
        orm_mode = True
class ActivityAttendance(BaseModel):

  child_id: int
  activity_id :int
  is_present:bool
  class Config:
        orm_mode = True
# Attendance Model
class Attendance(BaseModel):
    attendance_id: int
    child_id: int
    activity_id: int
    status: str
    checked_in_at: datetime
    is_present: bool
    class Config:
        orm_mode = True


# Notification Model
class Notification(BaseModel):
    notification_id: int
    user_id: int
    sent_by: Optional[int]
    message: str
    is_resolved: bool
    created_at: datetime
    reply_to: Optional[int]
    sent_by_name: Optional[str] = None  # Allow None if the name is not always present
    reply_to_message: Optional[str]  # הוספת שדה נוסף שישמור את ההודעה שאליה התגובה
    forward_reason:Optional[str]=None
    class Config:
        orm_mode = True
   



class Class(BaseModel):

    class_id :Optional[int]
    class_name: Optional[str]
    class Config:
        orm_mode = True


class ShirtSize(BaseModel):

    shirt_size_id:int
    shirt_size :str
    class Config:
        orm_mode = True
class BranchManagerWithLoginUser(BaseModel):
    branch_manager: BranchManager
    login_user: LoginUser

    class Config:
        orm_mode = True  
class ActivityGroups(BaseModel):
    activity_id: int
    group_id: int

    class Config:
        orm_mode = True