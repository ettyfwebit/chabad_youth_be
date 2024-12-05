from sqlalchemy import (
    Column, Integer, String, ForeignKey, Text, Date, DateTime, Boolean, CheckConstraint, func
)
from sqlalchemy.orm import relationship
from app.database import Base


# Role Model
class Role(Base):
    __tablename__ = "roles"

    role_id = Column(Integer, primary_key=True)
    role_name = Column(String(50), nullable=False, unique=True)
    login_users = relationship("LoginUser", back_populates="role", cascade="all, delete-orphan")


# Branch Model
class Branch(Base):
    __tablename__ = "branches"

    branch_id = Column(Integer, primary_key=True)
    branch_name = Column(String(100), nullable=False, unique=True)
    location = Column(String(255))
    created_at = Column(DateTime, default=func.now())
    activities = relationship("Activity", back_populates="branch")

# Notification Model
class Notification(Base):
    __tablename__ = "notifications"

    notification_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("login_users.login_user_id", ondelete="CASCADE"), nullable=False)
    sent_by = Column(Integer, ForeignKey("login_users.login_user_id", ondelete="SET NULL"), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())

    recipient = relationship("LoginUser", foreign_keys=[user_id], back_populates="notifications_received")
    sender = relationship("LoginUser", foreign_keys=[sent_by], back_populates="notifications_sent")

# Login User Model
class LoginUser(Base):
    __tablename__ = "login_users"

    login_user_id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.role_id", ondelete="RESTRICT"), nullable=False)
    created_at = Column(DateTime, default=func.now())

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

    child_id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey("parents.parent_id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    total_points = Column(Integer, default=0)

    parent = relationship("Parent", back_populates="children")
    attendance_records = relationship("Attendance", back_populates="child")



# Activity Model
class Activity(Base):
    __tablename__ = "activities"

    activity_id = Column(Integer, primary_key=True)
    branch_id = Column(Integer, ForeignKey("branches.branch_id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    location = Column(String(255))
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    points_awarded = Column(Integer, default=0)

    branch = relationship("Branch", back_populates="activities")
    attendance_records = relationship("Attendance", back_populates="activity")



# Attendance Model
class Attendance(Base):
    __tablename__ = "attendance"

    attendance_id = Column(Integer, primary_key=True)
    child_id = Column(Integer, ForeignKey("children.child_id", ondelete="CASCADE"), nullable=False)
    activity_id = Column(Integer, ForeignKey("activities.activity_id", ondelete="CASCADE"), nullable=False)
    status = Column(String(20), nullable=False)
    checked_in_at = Column(DateTime, default=func.now())

    __table_args__ = (
        CheckConstraint("status IN ('present', 'absent', 'late')", name="valid_status"),
    )

    child = relationship("Child", back_populates="attendance_records")
    activity = relationship("Activity", back_populates="attendance_records")



