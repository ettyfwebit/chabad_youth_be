from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime
from typing import Optional, List
from app import db_models, response_models, database

router = APIRouter(prefix="/activities", tags=["activities"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[response_models.Activity])
def get_activities(
    db: Session = Depends(get_db),
    name: Optional[str] = Query(None, description="Filter by activity name"),
    branch_id: Optional[int] = Query(None, description="Filter by branch ID"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date (YYYY-MM-DD)"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date (YYYY-MM-DD)"),
    min_points: Optional[int] = Query(None, description="Filter by minimum points"),
    max_points: Optional[int] = Query(None, description="Filter by maximum points"),
):
    """
    Get activities with optional filters.

    Filters:
    - `name`: Activity name (case-insensitive partial match)
    - `branch_id`: Branch ID
    - `start_date`, `end_date`: Date range
    - `min_points`, `max_points`: Range for points awarded
    """
    filters = []
    
    if name:
        filters.append(db_models.Activity.name.ilike(f"%{name}%"))
    if branch_id:
        filters.append(db_models.Activity.branch_id == branch_id)
    if start_date:
        filters.append(db_models.Activity.start_time >= start_date)
    if end_date:
        filters.append(db_models.Activity.end_time <= end_date)
    if min_points is not None:
        filters.append(db_models.Activity.points_awarded >= min_points)
    if max_points is not None:
        filters.append(db_models.Activity.points_awarded <= max_points)

    query = db.query(db_models.Activity)
    if filters:
        query = query.filter(and_(*filters))
    
    return query.all()

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

@router.get("/", response_model=List[response_models.Activity])
def get_activities(
    db: Session = Depends(get_db),
    name: Optional[str] = Query(None, description="Filter by activity name"),
    branch_id: Optional[int] = Query(None, description="Filter by branch ID"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date (YYYY-MM-DD)"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date (YYYY-MM-DD)"),
    min_points: Optional[int] = Query(None, description="Filter by minimum points"),
    max_points: Optional[int] = Query(None, description="Filter by maximum points"),
):
    filters = []
    if name:
        filters.append(db_models.Activity.name.ilike(f"%{name}%"))
    if branch_id:
        filters.append(db_models.Activity.branch_id == branch_id)
    if start_date:
        filters.append(db_models.Activity.start_time >= start_date)
    if end_date:
        filters.append(db_models.Activity.end_time <= end_date)
    if min_points is not None:
        filters.append(db_models.Activity.points_awarded >= min_points)
    if max_points is not None:
        filters.append(db_models.Activity.points_awarded <= max_points)

    query = db.query(db_models.Activity)
    if filters:
        query = query.filter(*filters)

    return query.all()


@router.post("/", response_model=response_models.Activity)
def create_activity(activity: request_models.ActivityCreate, db: Session = Depends(get_db)):
    """
    Create a new activity.
    """
    new_activity = db_models.Activity(
        branch_id=activity.branch_id,
        name=activity.name,
        description=activity.description,
        location=activity.location,
        start_time=activity.start_time,
        end_time=activity.end_time,
        points_awarded=activity.points_awarded,
    )
    db.add(new_activity)
    db.commit()
    db.refresh(new_activity)
    return new_activity


@router.put("/{activity_id}", response_model=response_models.Activity)
def edit_activity(
    activity_id: int, activity: request_models.ActivityEdit, db: Session = Depends(get_db)
):
    """
    Edit an existing activity.
    """
    existing_activity = db.query(db_models.Activity).filter(db_models.Activity.activity_id == activity_id).first()
    if not existing_activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    if activity.branch_id is not None:
        existing_activity.branch_id = activity.branch_id
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
    if activity.points_awarded is not None:
        existing_activity.points_awarded = activity.points_awarded

    db.commit()
    db.refresh(existing_activity)
    return existing_activity
