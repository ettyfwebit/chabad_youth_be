from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import db_models, request_models, response_models, database
from app.db_models import Notification
from app.messages import green_api

router = APIRouter(prefix="/notifications", tags=["notifications"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/{user_id}", response_model=List[response_models.Notification])
def get_notifications(user_id: int, db: Session = Depends(get_db)):
    notifications = (
        db.query(Notification, 
                 db_models.LoginUser.user_name.label('sent_by_name'),
                 Notification.notification_id,
                 Notification.message,
                 Notification.is_resolved,
                 Notification.created_at,
                 Notification.sent_by,
                 Notification.user_id)
        .join(db_models.LoginUser, Notification.sent_by == db_models.LoginUser.login_user_id)
        .filter(Notification.user_id == user_id)
        .order_by(Notification.is_resolved)
        .all()
    )

    return notifications


@router.post("/", response_model=list[response_models.Notification])
def send_notifications(request: request_models.messageRequest, db: Session = Depends(get_db)):
    notifications = []
    for user_id in request.user_ids:
        user = db.query(db_models.LoginUser).filter(db_models.LoginUser.login_user_id == user_id).first()
        green_api.send_message(request.message, user.chat_id)
        new_notification = Notification(
            user_id=user_id,
            sent_by=request.sent_by,
            message=request.message
        )
        db.add(new_notification)
        notifications.append(new_notification)
    db.commit()
    return notifications


@router.patch("/{notification_id}/mark_resolved")
def mark_as_resolved(notification_id: int, db: Session = Depends(get_db)):
    notification = db.query(Notification).filter(Notification.notification_id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    # Toggle the resolved state
    notification.is_resolved = not notification.is_resolved
    db.commit()
