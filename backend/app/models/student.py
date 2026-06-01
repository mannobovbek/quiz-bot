from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Float
from ..database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)
    score = Column(Integer, nullable=False, default=0)
    attempts_count = Column(Integer, default=0)
    avg_percentage = Column(Float, default=0.0)
    last_attempt_date = Column(DateTime, nullable=True)
    registered_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
