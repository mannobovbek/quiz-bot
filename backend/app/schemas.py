from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, conint

QuizOption = conint(ge=1, le=4)


class QuizBase(BaseModel):
    question: str = Field(..., min_length=5)
    option1: str = Field(..., min_length=1)
    option2: str = Field(..., min_length=1)
    option3: str = Field(..., min_length=1)
    option4: str = Field(..., min_length=1)
    correct: QuizOption


class QuizCreate(QuizBase):
    category_id: Optional[int] = None


class QuizUpdate(BaseModel):
    question: Optional[str]
    option1: Optional[str]
    option2: Optional[str]
    option3: Optional[str]
    option4: Optional[str]
    correct: Optional[QuizOption]


class QuizRead(QuizBase):
    id: int
    category_id: Optional[int] = None

    class Config:
        from_attributes = True




class StudentBase(BaseModel):
    name: str = Field(..., min_length=2)

    email: EmailStr
    score: int = Field(0, ge=0)


class StudentCreate(StudentBase):
    pass


class StudentRead(StudentBase):
    id: int
    registered_at: datetime

    class Config:
        from_attributes = True

class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1)
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryRead(CategoryBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
