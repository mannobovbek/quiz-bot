from __future__ import annotations

from datetime import datetime
import enum

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    Boolean,
    DateTime,
    Enum,
)
from sqlalchemy.orm import relationship

from ..database import Base


class QuizStatus(str, enum.Enum):
    # Keep exact DB string values
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"



class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)

    # v2 (professional quiz)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)

    time_limit = Column(Integer, default=0)  # in seconds, 0 = no limit
    shuffle_questions = Column(Boolean, default=False)
    shuffle_answers = Column(Boolean, default=False)
    show_result = Column(Boolean, default=True)
    # Store as plain string for stability (DB contains values like: 'draft')
    status = Column(String, default=QuizStatus.DRAFT.value)



    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Legacy fields (v1 quiz style)
    question = Column(String, nullable=True)
    option1 = Column(String, nullable=True)
    option2 = Column(String, nullable=True)
    option3 = Column(String, nullable=True)
    option4 = Column(String, nullable=True)
    correct = Column(Integer, nullable=True)

    category = relationship("Category", backref="quizzes")

