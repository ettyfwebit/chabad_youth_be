from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import db_models, response_models, database

router = APIRouter(prefix="/login_users", tags=["login_users"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=list[response_models.LoginUser])
def get_activities(db: Session = Depends(get_db)):
    return db.query(db_models.Activity).all()
