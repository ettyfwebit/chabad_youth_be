from fastapi import APIRouter, Depends, HTTPException
from psycopg2 import IntegrityError
from sqlalchemy.orm import Session
from app import db_models, response_models, database
router = APIRouter(prefix="/parents", tags=["parents"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()
@router.get("/", response_model=list[response_models.ParentsWithLoginUser])
def get_all_parents_with_login_users(db: Session = Depends(get_db)):
    result = []

    # שליפת כל המנהלי סניפים
    parents = db.query(db_models.Parent).all()

    for parent in parents:
        # שליפת משתמש הקשור לכל מנהל סניף
        login_user = db.query(db_models.LoginUser).filter(
            db_models.LoginUser.login_user_id == parent.login_user_id
        ).first()

        if login_user:
            # המרת הנתונים למודלים של Pydantic
            result.append(
                response_models.ParentsWithLoginUser(
                    parent=response_models.Parent.from_orm(parent),
                    login_user=response_models.LoginUser.from_orm(login_user),
                )
            )

    return result
