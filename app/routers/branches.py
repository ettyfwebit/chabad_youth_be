from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from psycopg2 import IntegrityError
from sqlalchemy.orm import Session
from app import db_models, request_models, response_models, database

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
@router.post("/addNewBranch", response_model=response_models.Branch)
def add_new_branch(newBranch: request_models.BranchCreate, db: Session = Depends(get_db)):
    new_branch = db_models.Branch(
        branch_name=newBranch.branch_name,
        location=newBranch.location,
        created_at=datetime.utcnow()
    )

    # הוספת הסניף למסד הנתונים
    db.add(new_branch)
    db.commit()
    db.refresh(new_branch)

    return new_branch

@router.put("/updateBranch", response_model=response_models.Branch)
def update_branch( updatedBranch: response_models.Branch, db: Session = Depends(get_db)):
    # חיפוש הסניף לפי ה-ID
    branch = db.query(db_models.Branch).filter(db_models.Branch.branch_id == updatedBranch.branch_id).first()

    if not branch:
        return {"error": "Branch not found"}

    # עדכון השדות שנשלחו, אם הועברו נתונים
    branch.branch_name = updatedBranch.branch_name if updatedBranch.branch_name else branch.branch_name
    branch.location = updatedBranch.location if updatedBranch.location else branch.location
    branch.created_at = updatedBranch.created_at if updatedBranch.location else branch.location
    # שמירת השינויים במסד הנתונים
    db.commit()
    db.refresh(branch)

    return branch
@router.delete("/deleteBranch/{branch_id}", response_model=response_models.Branch)
def delete_branch(branch_id: int, db: Session = Depends(get_db)):
    branch = db.query(db_models.Branch).filter(db_models.Branch.branch_id == branch_id).first()
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    
    db.delete(branch)
    db.commit()
    return branch
