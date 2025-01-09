from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import db_models, request_models, response_models, database
from app.db_models import Notification, Parent
from app.messages import green_api
from sqlalchemy import outerjoin
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import aliased
from sqlalchemy import create_engine



router = APIRouter(prefix="/notifications", tags=["notifications"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


from sqlalchemy.orm import joinedload

@router.get("/{user_id}", response_model=list[response_models.Notification])
def get_notifications(user_id: int, db: Session = Depends(get_db)):  
    # שליפת כל ההודעות עבור משתמש מסויים עם הצטרפות לטבלת Login_users
    notifications = (
        db.query(Notification, db_models.LoginUser.user_name.label("sent_by_name"))
        .join(db_models.LoginUser, Notification.sent_by == db_models.LoginUser.login_user_id)
        .options(joinedload(Notification.reply_to_notification))  # טוען את ההודעה שאליה התגובה מתייחסת
        .filter(Notification.user_id == user_id)
        .all()
    )

    # עיבוד התוצאה כדי למלא את השדה reply_to_message
    results = []
    for notification, sent_by_name in notifications:
        notification_data = notification.__dict__.copy()
        notification_data['reply_to_message'] = (
            notification.reply_to_notification.message if notification.reply_to_notification else None
        )
        notification_data['sent_by_name'] = sent_by_name  # הוספת השם של השולח
        results.append(notification_data)
    return results



@router.post("/sendNlotifications", response_model=list[response_models.Notification])
def send_notifications(request: request_models.messageRequest, db: Session = Depends(get_db)):
        print (request)
        notifications = []

        user = db.query(db_models.LoginUser).filter(db_models.LoginUser.login_user_id == request.user_ids).first()
        # אם מדובר בהודעה שהיא תגובה להודעה קודמת
        reply_to = request.reply_to_notification_id if hasattr(request, 'reply_to_notification_id') else None
        green_api.send_message(request.message, user.chat_id,request.forward_reason, reply_to_message_id=reply_to )
        new_notification = Notification(
            user_id=request.user_ids,
            sent_by=request.sent_by,
            message=request.message,
            reply_to=reply_to,
            forward_reason=request.forward_reason
        )
        db.add(new_notification)
        notifications.append(new_notification)
        db.commit()
        return notifications

@router.post("/", response_model=list[response_models.Notification])
def send_notifications(request: request_models.messagesRequest, db: Session = Depends(get_db)):
        print (request)
        notifications = []
        for user_id in request.user_ids:
         user = db.query(db_models.LoginUser).filter(db_models.LoginUser.login_user_id == user_id).first()
        # אם מדובר בהודעה שהיא תגובה להודעה קודמת
         reply_to = request.reply_to_notification_id if hasattr(request, 'reply_to_notification_id') else None
         green_api.send_message(request.message, user.chat_id, reply_to_message_id=reply_to)
         new_notification = Notification(
            user_id=user_id,
            sent_by=request.sent_by,
            message=request.message,
            reply_to=reply_to,
            forward_reason=request.forward_reason
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


@router.post("/login_ids", response_model=dict[int, int])
def get_login_user_ids(request: request_models.ParentIdRequest, db: Session = Depends(get_db)):
 
    print("parentId", request.parent_id)
    if not request.parent_id:
        raise HTTPException(status_code=400, detail="No parent_id provided")

    # שליפת הורה ותעודת המשתמש שלו
    parent = db.query(db_models.Parent.parent_id, db_models.Parent.login_user_id).filter(Parent.parent_id == request.parent_id).first()
    print("parent", parent)
    
    if parent:
        # מיפוי לתוצאה {parent_id: login_user_id}
        return {parent.parent_id: parent.login_user_id}
    else:
        raise HTTPException(status_code=404, detail="Parent not found")


