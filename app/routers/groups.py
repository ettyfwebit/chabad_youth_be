from fastapi import APIRouter, Depends, HTTPException
from psycopg2 import IntegrityError
from sqlalchemy.orm import Session
from app import db_models, response_models, database

router = APIRouter(prefix="/groups", tags=["groups"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()
@router.get("/", response_model=list[response_models.BranchGroup])
def get_branches(db: Session = Depends(get_db)):
    return db.query(db_models.BranchGroup).all()

@router.get("/getGroupsByBranchManager", response_model=list[response_models.BranchGroup])
def get_children(user_id: int,db: Session = Depends(get_db)):
    
    branchManager=db.query(db_models.BranchManager).filter(db_models.BranchManager.login_user_id==user_id).first()
    print(branchManager)
    groups= db.query(db_models.BranchGroup).filter(db_models.BranchGroup.branch_id ==branchManager.branch_id).all()
    return groups