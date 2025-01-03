from fastapi import APIRouter, Depends, HTTPException
from psycopg2 import IntegrityError
from sqlalchemy.orm import Session
from app import db_models, response_models, database

router = APIRouter(prefix="/branch_managers", tags=["branch_managers"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()



@router.get("/", response_model=list[response_models.BranchManagerWithLoginUser])
def get_all_branch_managers_with_login_users(db: Session = Depends(get_db)):
    result = []

    # שליפת כל המנהלי סניפים
    branch_managers = db.query(db_models.BranchManager).all()

    for branch_manager in branch_managers:
        # שליפת משתמש הקשור לכל מנהל סניף
        login_user = db.query(db_models.LoginUser).filter(
            db_models.LoginUser.login_user_id == branch_manager.login_user_id
        ).first()

        if login_user:
            # המרת הנתונים למודלים של Pydantic
            result.append(
                response_models.BranchManagerWithLoginUser(
                    branch_manager=response_models.BranchManager.from_orm(branch_manager),
                    login_user=response_models.LoginUser.from_orm(login_user),
                )
            )

    return result
@router.get("/{branch_manager_id}", response_model=response_models.BranchManager)
def get_branch_manager(branch_manager_id: int, db: Session = Depends(get_db)):
    # שליפת פרטי מנהל הסניף
    branch_manager = db.query(db_models.BranchManager).filter(db_models.BranchManager.branch_manager_id == branch_manager_id).first()
    if not branch_manager:
        raise HTTPException(status_code=404, detail="Branch manager not found")
    return branch_manager
