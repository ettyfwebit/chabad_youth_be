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

@router.get("/getChildrenByBranch", response_model=list[response_models.Child])
def get_children(user_id: int,db: Session = Depends(get_db)):
    branch_manager=db.query(db_models.BranchManager).filter(db_models.BranchManager.login_user_id==user_id).first()
    return db.query(db_models.Child).filter(db_models.Child.branch_manager_id == branch_manager.branch_manager_id).all()

@router.get("/getChildrenByParent", response_model=list[response_models.Child])
def get_children(user_id: int,db: Session = Depends(get_db)):
    parent=db.query(db_models.Parent).filter(db_models.Parent.login_user_id==user_id).first()
    return db.query(db_models.Child).filter(db_models.Child.parent_id == parent.parent_id).all()
    