from sqlalchemy import (
    Column, Integer, LargeBinary, String, ForeignKey, Text, Date, DateTime, Boolean, CheckConstraint,Sequence, func
)
from sqlalchemy.orm import relationship
from app.database import Base


# Role Model
class Role(Base):
    __tablename__ = "roles"

    role_id = Column(Integer, primary_key=True)
    role_name = Column(String(50), nullable=False, unique=True)
    login_users = relationship("LoginUser", back_populates="role", cascade="all, delete-orphan")



# Notification Model
class Notification(Base):
    __tablename__ = "notifications"

    notification_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("login_users.login_user_id", ondelete="CASCADE"), nullable=False)
    sent_by = Column(Integer, ForeignKey("login_users.login_user_id", ondelete="SET NULL"), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    reply_to= Column(Integer, ForeignKey('notifications.notification_id', ondelete="SET NULL"))
    forward_reason=Column(Text, nullable=True)  # עמודה שמפנה להודעה שאליה נכתבת התגובה
    reply_to_message=Column(String, nullable=True)
    # הגדרת קשר בין ההודעות (הודעה עונה להודעה אחרת)
    reply_to_notification = relationship("Notification", remote_side=[notification_id], foreign_keys=[reply_to])

    recipient = relationship("LoginUser", foreign_keys=[user_id], back_populates="notifications_received")
    sender = relationship("LoginUser", foreign_keys=[sent_by], back_populates="notifications_sent")

# Login User Model
class LoginUser(Base):
    __tablename__ = "login_users"

    login_user_id = Column(Integer, primary_key=True)
    user_name = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.role_id", ondelete="RESTRICT"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    phone = Column(String(50), nullable=False, unique=True)
    chat_id=Column(String(50),nullable=True)
    role = relationship("Role", back_populates="login_users")
    notifications_received = relationship(
        "Notification",
        foreign_keys=[Notification.user_id],
        back_populates="recipient",
        cascade="all, delete-orphan"
    )

    # קשר לשליחת הודעות (notifications_sent)
    notifications_sent = relationship(
        "Notification",
        foreign_keys=[Notification.sent_by],
        back_populates="sender",
        cascade="all, delete-orphan"
    )
class ActivityAttendance(Base):
    __tablename__ = "activity_attendance"
    child_id = Column(Integer, ForeignKey("children.child_id", ondelete="CASCADE"), nullable=False, primary_key=True)
    activity_id = Column(Integer, ForeignKey("activities.activity_id", ondelete="CASCADE"), nullable=False, primary_key=True)
    is_present=Column(Boolean)
    child = relationship("Child", back_populates="activity_attendance")  # הקשר עם השם החדש
    activity = relationship("Activity", back_populates="attendance_records")


# Parent Model
class Parent(Base):
    __tablename__ = "parents"

    parent_id = Column(Integer, primary_key=True)
    login_user_id = Column(Integer, ForeignKey("login_users.login_user_id", ondelete="CASCADE"), nullable=False, unique=True)
    additional_info = Column(Text)
    children = relationship("Child", back_populates="parent", cascade="all, delete-orphan")

    login_user = relationship("LoginUser")


# Branch Manager Model
class BranchManager(Base):
    __tablename__ = "branch_managers"

    branch_manager_id = Column(Integer, primary_key=True)
    login_user_id = Column(Integer, ForeignKey("login_users.login_user_id", ondelete="CASCADE"), nullable=False, unique=True)
    branch_id = Column(Integer, ForeignKey("branches.branch_id", ondelete="SET NULL"))
    additional_info = Column(Text)

    children = relationship("Child", back_populates="branch_manager")
    login_user = relationship("LoginUser")
    branch = relationship("Branch")


# Secretary Model
class Secretary(Base):
    __tablename__ = "secretaries"

    secretary_id = Column(Integer, primary_key=True)
    login_user_id = Column(Integer, ForeignKey("login_users.login_user_id", ondelete="CASCADE"), nullable=False, unique=True)
    additional_info = Column(Text)

    login_user = relationship("LoginUser")



# Child Model
class Child(Base):
    __tablename__ = "children"


    child_id = Column(Integer,unique=True,  primary_key=True)
    parent_id = Column(Integer, ForeignKey('parents.parent_id'), nullable=True)
    branch_group_id = Column(Integer, ForeignKey('branch_groups.group_id'))
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100))
    nickname = Column(String(100))
    date_of_birth = Column(Date, nullable=True)
    id_number = Column(String(20), unique=True)
    phone = Column(String(15))
    school_name = Column(String(100))
    street = Column(String(100))
    house_number = Column(String(10))
    city = Column(String(50))
    parent_email = Column(String(100))
    mother_name = Column(String(100))
    mother_phone = Column(String(15))
    father_name = Column(String(100))
    father_phone = Column(String(15))
    health_issue = Column(Boolean, default=False)
    approval_received = Column(Boolean, default=False)
    branch_id = Column(Integer, ForeignKey('branches.branch_id'))
    class_id = Column(Integer, ForeignKey('classes.class_id'))
    shirt_size_id = Column(Integer, ForeignKey('shirt_sizes.shirt_size_id'))
    total_points = Column(Integer, default=0)
    branch_manager_id = Column(Integer, ForeignKey('branch_managers.branch_manager_id'))
    image=Column(LargeBinary)
        # Relationships
    meeting_attendance = relationship("Attendance", back_populates="child" ,cascade="all, delete")
    activity_attendance = relationship("ActivityAttendance", back_populates="child")
    branch_manager = relationship('BranchManager', back_populates='children')
    branch = relationship('Branch', back_populates='children')
    class_ = relationship('Class', back_populates='children')
    shirt = relationship('ShirtSize', back_populates='children')
    parent = relationship('Parent', back_populates='children')


# Activity Model
class Activity(Base):
    __tablename__ = "activities"

    activity_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    location = Column(String(255))
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    points_limit = Column(Integer, default=0)

    attendance_records = relationship("ActivityAttendance", back_populates="activity")
    activity_groups = relationship("ActivityGroup", back_populates="activity")


# Attendance Model
class Attendance(Base):
    __tablename__ = "attendance"

    attendance_id = Column(Integer, primary_key=True)
    child_id = Column(Integer, ForeignKey("children.child_id", ondelete="CASCADE"), nullable=False)
    is_present=Column(Boolean)
    meeting_id = Column(Integer, ForeignKey("meetings.meeting_id", ondelete="CASCADE"), nullable=False)    
    branch_id= Column(Integer, nullable=False)
    checked_in_at = Column(DateTime, default=func.now())
    child = relationship("Child", back_populates="meeting_attendance") 
    meeting = relationship("Meeting", back_populates="attendance_records")

# Branch Model
class Branch(Base):
    __tablename__ = "branches"

    branch_id = Column(Integer, primary_key=True)
    branch_name = Column(String(100), nullable=False, unique=True)
    location = Column(String(255))
    created_at = Column(DateTime, default=func.now())
    children = relationship('Child', back_populates='branch')
    branch_groups = relationship('BranchGroup', back_populates='branch')

class Class(Base):
    __tablename__ = 'classes'

    class_id = Column(Integer, primary_key=True)
    class_name = Column(String(100), unique=True, nullable=False)

    # Relationships
    children = relationship('Child', back_populates='class_')



# טבלת הקשרים בין Meetings ו-BranchGroups
class MeetingBranchGroup(Base):
    __tablename__ = 'meeting_branch_groups'

    meeting_id = Column(Integer, ForeignKey('meetings.meeting_id', ondelete='CASCADE'), primary_key=True)
    group_id = Column(Integer, ForeignKey('branch_groups.group_id', ondelete='CASCADE'), primary_key=True)

class BranchGroup(Base):
    __tablename__ = 'branch_groups'

    group_id = Column(Integer, primary_key=True)
    group_name = Column(String(100), nullable=True)
    branch_id = Column(Integer, ForeignKey('branches.branch_id'))  # ForeignKey מקשר לטבלה branches

    # Relationships
    meetings = relationship(
        'Meeting',
        secondary='meeting_branch_groups',
        back_populates='branch_groups'
    )
    
    branch = relationship("Branch", back_populates="branch_groups")  # קשר חדש
    children = relationship('Child', backref='group_of_children')
    activity_groups = relationship("ActivityGroup", back_populates="group")



class Meeting(Base):
    __tablename__ = 'meetings'

    meeting_id = Column(Integer, primary_key=True)
    meeting_name = Column(String(100), nullable=True)
    meeting_date = Column(DateTime, default=func.now())


    # Relationships
    branch_groups = relationship(
        'BranchGroup', 
        secondary='meeting_branch_groups',  # כאן אנו מציינים את שם טבלת הקשרים
        back_populates='meetings'
    )
    attendance_records = relationship("Attendance", back_populates="meeting")

 

class ShirtSize(Base):
    __tablename__ = 'shirt_sizes'

    shirt_size_id = Column(Integer, primary_key=True)
    shirt_size = Column(String(20), unique=True, nullable=False)

    # Relationships
    children = relationship('Child', back_populates='shirt')

class ActivityGroup(Base):
    __tablename__ = 'activity_groups'

    activity_id = Column(Integer, ForeignKey('activities.activity_id'), primary_key=True)
    group_id = Column(Integer, ForeignKey('branch_groups.group_id'), primary_key=True)

    # קשרים בין הטבלאות (אם יש קשרים נוספים)
    activity = relationship("Activity", back_populates="activity_groups")
    group = relationship("BranchGroup", back_populates="activity_groups")
