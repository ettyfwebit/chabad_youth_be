from fastapi import APIRouter, Depends, HTTPException
from psycopg2 import IntegrityError
from sqlalchemy.orm import Session
from app import db_models, response_models, database

router = APIRouter(prefix="/meetings", tags=["meetings"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()
@router.post("/createNewMeeting")
def create_meeting( meetingName: dict, db: Session = Depends(get_db)):
    print(meetingName.get("meeting_name"))
    new_meeting = db_models.Meeting(meeting_name=meetingName.get("meeting_name"))
    db.add(new_meeting)
    db.commit()
    db.refresh(new_meeting)
    return {"meeting_id": new_meeting.meeting_id}
