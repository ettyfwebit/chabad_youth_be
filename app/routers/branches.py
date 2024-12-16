from fastapi import APIRouter, Depends, HTTPException
from psycopg2 import IntegrityError
from sqlalchemy.orm import Session
from app import db_models, response_models, database

router = APIRouter(prefix="/branches", tags=["branches"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()
@router.get("/", response_model=list[response_models.Branch])
def get_branches(db: Session = Depends(get_db)):
    return db.query(db_models.Branch).all()