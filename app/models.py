
from sqlalchemy import Column, Integer, String, ForeignKey, Date
from app.database import Base

class Child(Base):
    __tablename__ = "children"

    child_id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    name = Column(String, nullable=False)
    date_of_birth = Column(Date, nullable=False)
    total_points = Column(Integer, default=0)
