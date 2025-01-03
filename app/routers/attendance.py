from fastapi import APIRouter, Depends, HTTPException
from psycopg2 import IntegrityError
from sqlalchemy.orm import Session
from app import db_models, response_models, database

router = APIRouter(prefix="/attendance", tags=["attendance"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()
              
@router.post("/updateAttendance")
def update_attendance(attendance_data: dict, db: Session = Depends(get_db)):
    # Example of attendance_data: {child_id: is_present, ...}
    for child_id, data in attendance_data.items():
        print(child_id)
        print(data)
        new_attendance =db_models.Attendance(
          child_id=child_id,
          is_present=data.get("is_present"),
          meeting_id=data.get("meeting_id"),
          branch_id=data.get("branch_id"),
            )
        db.add(new_attendance)

        # שמירה במסד נתונים
    db.commit()

    return {"status": "success", "message": "Attendance updated successfully"}
@router.post("/activityAttendance")
def save_attendance(attendance: list[dict], db: Session = Depends(get_db)):
    """
    Save attendance data for the given activity.
    """
    try:
        for entry in attendance:
            activity_id = entry['activity_id']
            child_id = entry['child_id']
            is_present = entry['is_present']

            # בדוק אם יש כבר רישום לנוכחות של הילד לפעילות הזו
            existing_record = db.query(db_models.ActivityAttendance).filter(
                db_models.ActivityAttendance.activity_id == activity_id,
                db_models.ActivityAttendance.child_id == child_id
            ).first()

            if existing_record:
                # עדכון אם כבר יש רישום קיים
                existing_record.is_present = is_present
            else:
                # הוספה של רישום חדש אם אין כזה
                new_record = db_models.ActivityAttendance(
                    activity_id=activity_id,
                    child_id=child_id,
                    is_present=is_present
                )
                db.add(new_record)

        db.commit()  # שמירה
        return {"message": "Attendance data saved successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

