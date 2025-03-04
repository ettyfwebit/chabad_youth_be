
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
from app.routers import attendance, branch_managers, branches, children, activities, classgrades, groups, login_users, meetings, notifications, parents, shirts
from app.database import Base, engine
from fastapi.staticfiles import StaticFiles
import os
from sqlalchemy.orm import Session
from app.database import SessionLocal
from fastapi.responses import RedirectResponse
from fastapi import status


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# יצירת מפתחות עבור JWT
SECRET_KEY = "your_secret_key_here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

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






# Create tables

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development (use specific domains in production)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)


import os
app.mount("/static", StaticFiles(directory=os.path.join("C:\\", "Users", "Riky", "Desktop", "chabad_youth_fe", "build", "static")), name="static")

# מסלול עבור קובץ ה-HTML הראשי של React
@app.get("/")
async def index():
    return FileResponse(os.path.join(os.getcwd(), "C:\\", "Users", "Riky", "Desktop", "chabad_youth_fe","build", "index.html"))

# Include routers
app.include_router(children.router)
app.include_router(activities.router)
app.include_router(login_users.router)
app.include_router(notifications.router)
app.include_router(branches.router)
app.include_router(classgrades.router)
app.include_router(shirts.router)
app.include_router(groups.router)
app.include_router(meetings.router)
app.include_router(attendance.router)
app.include_router(branch_managers.router)
app.include_router(parents.router)

# ניתוב מחדש לבקשות שאינן מזוהות אל דף ה-React
@app.get("/{full_path:path}")
async def catch_all(full_path: str):
    return FileResponse(os.path.join(os.getcwd(), "C:\\", "Users", "Riky", "Desktop", "chabad_youth_fe", "build", "index.html"))

# נתיב לקבלת Token
@app.post("/auth/token")
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    # אימות פרטי המשתמש
    user = login_users.login_user(
        request_models.LoginRequest(user_name=form_data.username, password=form_data.password),
        db=db,
    )
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # הוספת role ל-token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": str(user["user_id"]),  # מזהה המשתמש
            "role": user["role"],        # role של המשתמש
        },
        expires_delta=access_token_expires,
    )

    # החזרת token והמידע הנוסף
    return {"access_token": access_token, "token_type": "bearer", "user": user}

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
