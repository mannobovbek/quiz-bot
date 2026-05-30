from typing import Optional

from pydantic import BaseModel, Field, conint

QuizOption = conint(ge=1, le=4)


class QuizBase(BaseModel):
    question: str = Field(..., min_length=1)
    option1: str = Field(..., min_length=1)
    option2: str = Field(..., min_length=1)
    option3: str = Field(..., min_length=1)
    option4: str = Field(..., min_length=1)
    correct: QuizOption


class QuizCreate(QuizBase):
    pass


class QuizUpdate(BaseModel):
    question: Optional[str]
    option1: Optional[str]
    option2: Optional[str]
    option3: Optional[str]
    option4: Optional[str]
    correct: Optional[QuizOption]


class QuizRead(QuizBase):
    id: int

    class Config:
        orm_mode = True
