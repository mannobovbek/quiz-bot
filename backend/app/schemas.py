from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr, Field, conint

QuizOption = conint(ge=1, le=4)

# ==================== LEGACY SCHEMAS ====================

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


# ==================== ANSWER SCHEMAS ====================

class AnswerCreate(BaseModel):
    text: str = Field(..., min_length=1)
    is_correct: bool = False


class AnswerUpdate(BaseModel):
    text: Optional[str] = None
    is_correct: Optional[bool] = None


class AnswerRead(BaseModel):
    id: int
    question_id: int
    text: str
    is_correct: bool

    class Config:
        from_attributes = True


class AnswerReadWithoutCorrect(BaseModel):
    """For showing to students - hides correct answer"""
    id: int
    text: str

    class Config:
        from_attributes = True


# ==================== QUESTION SCHEMAS ====================

class QuestionCreate(BaseModel):
    text: str = Field(..., min_length=5)
    image_url: Optional[str] = None
    points: int = Field(1, ge=1)
    order_number: int = Field(..., ge=0)
    answers: List[AnswerCreate] = Field(..., min_items=2, max_items=10)


class QuestionUpdate(BaseModel):
    text: Optional[str] = None
    image_url: Optional[str] = None
    points: Optional[int] = None
    order_number: Optional[int] = None
    answers: Optional[List[AnswerCreate]] = None


class QuestionRead(BaseModel):
    id: int
    quiz_id: int
    text: str
    image_url: Optional[str]
    points: int
    order_number: int
    answers: List[AnswerRead]
    created_at: datetime

    class Config:
        from_attributes = True


class QuestionReadForStudent(BaseModel):
    """For students taking the quiz - hides correct answers"""
    id: int
    text: str
    image_url: Optional[str]
    points: int
    answers: List[AnswerReadWithoutCorrect]

    class Config:
        from_attributes = True


# ==================== NEW QUIZ SCHEMAS ====================

class QuizCreateNew(BaseModel):
    title: str = Field(..., min_length=3)
    description: Optional[str] = None
    category_id: Optional[int] = None
    time_limit: int = Field(0, ge=0)  # 0 = no limit
    shuffle_questions: bool = False
    shuffle_answers: bool = False
    show_result: bool = True


class QuizUpdateNew(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    time_limit: Optional[int] = None
    shuffle_questions: Optional[bool] = None
    shuffle_answers: Optional[bool] = None
    show_result: Optional[bool] = None
    status: Optional[str] = None  # draft, published, archived


class QuizReadNew(BaseModel):
    id: int
    title: str
    description: Optional[str]
    category_id: Optional[int]
    time_limit: int
    shuffle_questions: bool
    shuffle_answers: bool
    show_result: bool
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class QuizReadFull(QuizReadNew):
    """Full quiz with all questions for admin"""
    questions: List[QuestionRead] = []


class QuizReadForStudent(BaseModel):
    """Quiz for students - hides correct answers"""
    id: int
    title: str
    description: Optional[str]
    time_limit: int
    questions: List[QuestionReadForStudent] = []

    class Config:
        from_attributes = True


# ==================== STUDENT SCHEMAS ====================

class StudentBase(BaseModel):
    name: str = Field(..., min_length=2)
    email: EmailStr
    score: int = Field(0, ge=0)


class StudentCreate(StudentBase):
    pass


class StudentRead(StudentBase):
    id: int
    attempts_count: int
    avg_percentage: float
    last_attempt_date: Optional[datetime]
    registered_at: datetime

    class Config:
        from_attributes = True


# ==================== CATEGORY SCHEMAS ====================

class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1)
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryRead(CategoryBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== QUIZ ATTEMPT SCHEMAS ====================

class AttemptAnswerSubmit(BaseModel):
    question_id: int
    selected_answer_id: int


class QuizAttemptStart(BaseModel):
    quiz_id: int


class QuizAttemptSubmitAnswer(BaseModel):
    attempt_id: int
    question_id: int
    selected_answer_id: int


class QuizAttemptFinish(BaseModel):
    attempt_id: int


class QuizAttemptRead(BaseModel):
    id: int
    student_id: int
    quiz_id: int
    started_at: datetime
    finished_at: Optional[datetime]
    score: int
    percentage: float
    correct_count: int
    wrong_count: int
    duration: int

    class Config:
        from_attributes = True


class AttemptAnswerRead(BaseModel):
    id: int
    attempt_id: int
    question_id: int
    selected_answer_id: int
    is_correct: bool
    answered_at: datetime

    class Config:
        from_attributes = True


class QuizAttemptDetailRead(QuizAttemptRead):
    """Attempt with all answers for admin review"""
    answers: List[AttemptAnswerRead] = []


# ==================== LEGACY SCHEMAS ====================

class QuizSubmitRequest(BaseModel):
    quiz_id: int
    student_name: str = Field(..., min_length=2)
    student_email: EmailStr
    selected_option_id: QuizOption


class QuizSubmitResponse(BaseModel):
    quiz_id: int
    student_email: EmailStr
    correct: bool
    score: int

