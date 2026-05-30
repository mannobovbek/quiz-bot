from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String
from ..database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)
    score = Column(Integer, nullable=False, default=0)
    registered_at = Column(DateTime, default=datetime.utcnow)
