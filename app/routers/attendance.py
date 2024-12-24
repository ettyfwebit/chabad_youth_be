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

