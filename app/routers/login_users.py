from fastapi import APIRouter, Depends, HTTPException
import psycopg2
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
    upload_image_to_db(40, r"C:\Users\ריקי\Downloads\DSC03774.jpg", db)

    user = db.query(db_models.LoginUser).filter(db_models.LoginUser.user_name == request.user_name).first()    
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
    register_request: request_models.RegisterRequest,  # Use RegisterRequest as the input
    db: Session = Depends(get_db)
):
    """
    Register a new user.
    
    Args:
        register_request: The registration data (user_name, email, password, role_id).
        db: Database session (injected).

    Returns:
        The newly created user details, excluding the password.
    """
    user_name = register_request.user_name
    email = register_request.email
    password = register_request.password
    role_id = register_request.role_id

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
 

from sqlalchemy.exc import SQLAlchemyError

def upload_image_to_db(child_id: int, image_path: str, db: Session):
 
    try:
        with open(image_path, "rb") as file:
            image_data = file.read()
        print(f"Image updated for child with ID {child_id}")  # לוג של השינוי
        # Update the children table
        query = db.query(db_models.Child).filter(db_models.Child.child_id == child_id).first()
        if query:
            query.image = image_data  # Update the image column
            db.commit()
            print(f"Commit successful for child with ID {child_id}")  # לוג אחרי הcommit

        else:
            raise ValueError(f"Child with ID {child_id} not found")
    except (SQLAlchemyError, IOError) as e:
        db.rollback()  # Rollback the transaction in case of error
        raise HTTPException(status_code=500, detail=str(e))
