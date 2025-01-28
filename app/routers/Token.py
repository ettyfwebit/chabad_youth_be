from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from app.routers import attendance, branch_managers, branches, children, activities, classgrades, groups, login_users, meetings, notifications, parents, shirts
from app.database import Base, engine
from fastapi.staticfiles import StaticFiles
import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from app import request_models
from app.database import Base, engine
from fastapi.staticfiles import StaticFiles
import os
from sqlalchemy.orm import Session
from app.database import SessionLocal
from fastapi.responses import RedirectResponse
from fastapi import status

# יצירת מפתחות עבור JWT
SECRET_KEY = "your_secret_key_here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
# פונקציה ליצירת Token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# OAuth2PasswordBearer להגדרת ה-endpoint לקבלת ה-token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# פונקציה לאימות Token
def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=401, detail="Invalid authentication credentials"
            )
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

# יצירת טבלאות בבסיס הנתונים
Base.metadata.create_all(bind=engine)


def get_current_role(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        role: str = payload.get("role")
        if role is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return role
def role_required(required_role: str):
    def _role_required(current_role: str = Depends(get_current_role)):
        if current_role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have the required role",
            )
        return current_role
    return _role_required





