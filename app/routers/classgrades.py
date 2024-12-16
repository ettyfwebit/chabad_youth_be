from fastapi import APIRouter, Depends, HTTPException
from psycopg2 import IntegrityError
from sqlalchemy.orm import Session
from app import db_models, response_models, database

router = APIRouter(prefix="/classgrades", tags=["classgrades"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()
@router.get("/", response_model=list[response_models.Class])
def get_classes(db: Session = Depends(get_db)):
    return db.query(db_models.Class).all()