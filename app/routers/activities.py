from warnings import filters
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime
from typing import Optional, List
from app import db_models, response_models, database
from app.routers.Token import role_required
from app.routers.Token import verify_token

router = APIRouter(prefix="/activities", tags=["activities"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()



from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app import db_models, response_models, database, request_models

router = APIRouter(prefix="/activities", tags=["activities"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/checkPermission")
def checkPermission(db: Session = Depends(get_db),str = Depends(role_required("branch_manager"))):
    return
@router.get("/checkParentPermission")
def checkPermission(db: Session = Depends(get_db),str = Depends(role_required("parent"))):
    return

@router.get("/checkSecretaryPermission")
def checkPermission(db: Session = Depends(get_db),str = Depends(role_required("secretary"))):
    return

@router.post("/", response_model=response_models.Activity)
def create_activity(activity: request_models.ActivityCreate, db: Session = Depends(get_db) ,str = Depends(role_required("secretary"))):
    """
    Create a new activity.
    """
    new_activity = db_models.Activity(
        name=activity.name,
        description=activity.description,
        location=activity.location,
        start_time=activity.start_time,

        end_time=activity.end_time,

    )
    db.add(new_activity)
    db.commit()
    db.refresh(new_activity)
    return new_activity
@router.put("/updateActivity", response_model=response_models.Activity)
def update_activity(activity_data: response_models.ActivityWithBranches, db: Session = Depends(get_db), str = Depends(role_required("secretary"))):
        print (activity_data)
        # חיפוש הילד במאגר
        activity = db.query(db_models.Activity).filter(db_models.Activity.activity_id == activity_data.activity_id).first()

        if not activity:
            raise HTTPException(status_code=404, detail="Activity not found")

        # עדכון שדות הילד
        activity.activity_id=activity_data.activity_id
        activity.name=activity_data.name
        activity.description=activity_data.description
        activity.location=activity_data.location
        activity.start_time=activity_data.start_time
        activity.end_time=activity_data.end_time
        db.commit()
        db.refresh(activity)
        return activity

@router.put("/{activity_id}", response_model=response_models.Activity )
def edit_activity(
    activity_id: int, activity: request_models.ActivityEdit, db: Session = Depends(get_db) ,str = Depends(verify_token)
):
    """
    Edit an existing activity.
    """
    existing_activity = db.query(db_models.Activity).filter(db_models.Activity.activity_id == activity_id).first()
    if not existing_activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    
    if activity.name is not None:
        existing_activity.name = activity.name
    if activity.description is not None:
        existing_activity.description = activity.description
    if activity.location is not None:
        existing_activity.location = activity.location
    if activity.start_time is not None:
        existing_activity.start_time = activity.start_time
    if activity.end_time is not None:
        existing_activity.end_time = activity.end_time
  

    db.commit()
    db.refresh(existing_activity)
    return existing_activity
@router.post("/{activity_id}/groups", response_model=List[response_models.ActivityGroups])
def update_activity_groups(activity_id: int, group_ids: List[int], db: Session = Depends(get_db) ,role: str = Depends(role_required("secretary"))
):
    print(f"Received activity_id: {activity_id}, group_ids: {group_ids}")  # הדפס את הנתונים שהתקבלו

    # בדיקת קיום הפעילות
    existing_activity = db.query(db_models.Activity).filter(db_models.Activity.activity_id == activity_id).first()
    if not existing_activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    # שליפת כל הקבוצות הקיימות עבור הפעילות
    existing_groups = db.query(db_models.ActivityGroup).filter(db_models.ActivityGroup.activity_id == activity_id).all()
    existing_group_ids = {group.group_id for group in existing_groups}

    # מחיקת קבוצות שלא נבחרו יותר
    groups_to_remove = existing_group_ids - set(group_ids)
    if groups_to_remove:
        db.query(db_models.ActivityGroup).filter(
            db_models.ActivityGroup.activity_id == activity_id,
            db_models.ActivityGroup.group_id.in_(groups_to_remove)
        ).delete(synchronize_session=False)

    # הוספת קבוצות חדשות שנבחרו בלבד אם הן לא קיימות
    groups_to_add = set(group_ids) - existing_group_ids
    for group_id in groups_to_add:
        existing_group = db.query(db_models.BranchGroup).filter(db_models.BranchGroup.group_id == group_id).first()
        if not existing_group:
            raise HTTPException(status_code=404, detail=f"Group {group_id} not found")

        new_activity_group = db_models.ActivityGroup(activity_id=activity_id, group_id=group_id)
        db.add(new_activity_group)

    db.commit()

    # שליפת רשימת הקבוצות המעודכנת והחזרתה
    updated_groups = db.query(db_models.ActivityGroup).filter(db_models.ActivityGroup.activity_id == activity_id).all()
    return updated_groups


@router.get("/", response_model=List[response_models.ActivityWithBranches])
def get_activities(db: Session = Depends(get_db),str = Depends(role_required("secretary"))):
    query = (
        db.query(
            db_models.Activity,
            db_models.BranchGroup,
            db_models.Branch
        )
        .join(db_models.ActivityGroup, db_models.Activity.activity_id == db_models.ActivityGroup.activity_id)
        .join(db_models.BranchGroup, db_models.ActivityGroup.group_id == db_models.BranchGroup.group_id)
        .join(db_models.Branch, db_models.BranchGroup.branch_id == db_models.Branch.branch_id)
        .all()
    )

    activity_dict = {}
    for activity, group, branch in query:
        if activity.activity_id not in activity_dict:
            activity_dict[activity.activity_id] = {
                "activity_id": activity.activity_id,
                "name": activity.name,
                "description": activity.description,
                "location": activity.location,
                "start_time": activity.start_time,
                "end_time": activity.end_time,
                "branches": {}
            }

        # בדיקה אם הסניף כבר נוסף תחת הפעילות
        if branch.branch_id not in activity_dict[activity.activity_id]["branches"]:
            activity_dict[activity.activity_id]["branches"][branch.branch_id] = {
                "branch_name": branch.branch_name,
                "branch_id":branch.branch_id,
                "groups": []
            }

        # בדיקה אם הקבוצה כבר נוספה לסניף
        existing_groups = activity_dict[activity.activity_id]["branches"][branch.branch_id]["groups"]
        if not any(g["group_id"] == group.group_id for g in existing_groups):
            activity_dict[activity.activity_id]["branches"][branch.branch_id]["groups"].append({
                "group_id": group.group_id,
                "group_name": group.group_name,
                "branch_id": group.branch_id,
            })

    # שינוי מילון לרשימה בפורמט הנדרש
    for activity in activity_dict.values():
        activity["branches"] = list(activity["branches"].values())

    return list(activity_dict.values())


@router.delete("/deleteActivity/{activity_id}")
def delete_child(activity_id: int, db: Session = Depends(get_db),str = Depends(verify_token)):
    # חיפוש הילד לפי ID
    activity = db.query(db_models.Activity).filter(db_models.Activity.activity_id == activity_id).first()
    
    if not activity:
        # אם הילד לא נמצא, מחזירים שגיאה
        raise HTTPException(status_code=404, detail="Child not found")
    
    # מחיקת הילד מהטבלה
    db.delete(activity)
    db.commit()
    return {"status": "success"}