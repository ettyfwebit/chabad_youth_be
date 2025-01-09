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

@router.get("/{branch_id}/groups", response_model=list[response_models.BranchGroup])
def get_branch_groups(branch_id: int, db: Session = Depends(get_db)):
    group_list=db.query(db_models.BranchGroup).filter(db_models.BranchGroup.branch_id==branch_id)
   
    # החזרת קבוצות הסניף
    return group_list

@router.post("/{branch_id}/groups", response_model=response_models.BranchGroup)
def add_group_to_branch(branch_id: int, new_group: request_models.BranchGroupCreate, db: Session = Depends(get_db)):
    # חיפוש הסניף
    branch = db.query(db_models.Branch).filter(db_models.Branch.branch_id == branch_id).first()
    
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")

    # יצירת קבוצה חדשה
    new_group_db = db_models.BranchGroup(
        group_name=new_group.group_name,
        branch_id=branch_id
    )
    db.add(new_group_db)
    db.commit()
    db.refresh(new_group_db)
    
    return new_group_db
@router.put("/groups", response_model=list[response_models.BranchGroup])
def update_group(updated_groups: list[response_models.BranchGroup], db: Session = Depends(get_db)):
    updated_result = []
    
    for group in updated_groups:
        # חפש את הקבוצה לפי ה-group_id
        match_group = db.query(db_models.BranchGroup).filter(db_models.BranchGroup.group_id == group.group_id).first()

        if not match_group:
            raise HTTPException(status_code=404, detail="Group not found")
        
        # עדכון שם הקבוצה
        match_group.group_name = group.group_name if group.group_name else match_group.group_name

        db.commit()
        db.refresh(match_group)
        
        updated_result.append(match_group)
    
    return updated_result

@router.delete("/groups/{group_id}", response_model=response_models.BranchGroup)
def delete_group(group_id: int, db: Session = Depends(get_db)):
    group = db.query(db_models.BranchGroup).filter(db_models.BranchGroup.group_id == group_id).first()

    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    db.delete(group)
    db.commit()

    return group
