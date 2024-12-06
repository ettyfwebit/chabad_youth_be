from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import db_models, response_models, database

router = APIRouter(prefix="/children", tags=["children"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=list[response_models.Child])
def get_children(db: Session = Depends(get_db)):
    return db.query(db_models.Child).all()
