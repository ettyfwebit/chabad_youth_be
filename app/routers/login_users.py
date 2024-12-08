from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app import db_models, request_models, response_models, database

router = APIRouter(prefix="/auth", tags=["auth"])

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

@router.post("/login")


def login_user(request:request_models.LoginRequest , db: Session = Depends(get_db)):
    """
    Validate user credentials.

    Args:
        user_name: The user_name provided by the user.
        password: The password provided by the user.
        db: Database session (injected).

    Returns:
        A dictionary with success status and the user's role if validation is successful.
    """
   

    user = db.query(db_models.LoginUser).filter(db_models.LoginUser.username == request.user_name).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user_name or password")

    if not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid user_name or password")
    
    # Fetch the role name
    role = db.query(db_models.Role).filter(db_models.Role.role_id == user.role_id).first()
    if not role:
        raise HTTPException(status_code=500, detail="Role not found for user")
    
    return {"success": True, "role": role.role_name, "user_id":user.login_user_id}


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


@router.post("/register", response_model=response_models.LoginUser)
def register_user(
    user_name: str, 
    email: str, 
    password: str, 
    role_id: int, 
    db: Session = Depends(get_db)
):
    """
    Register a new user.
    
    Args:
        user_name: The user_name for the new user.
        email: The email for the new user.
        password: The plain-text password for the new user.
        role_id: The ID of the role assigned to the user.
        db: Database session (injected).

    Returns:
        The newly created user details, excluding the password.
    """
    # Check if user_name or email already exists
    existing_user = db.query(db_models.LoginUser).filter(
        (db_models.LoginUser.user_name == user_name) | (db_models.LoginUser.email == email)
    ).first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="user_name or email already exists")

    # Hash the password
    hashed_password = hash_password(password)

    # Create a new user object
    new_user = db_models.LoginUser(
        user_name=user_name,
        email=email,
        password_hash=hashed_password,
        role_id=role_id,
    )

    # Add the user to the database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Return the user details
    return new_user
