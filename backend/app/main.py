from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
from sqlalchemy.orm import Session

from .database import Base, SessionLocal, engine
from .models.quiz import Quiz
from .models.student import Student
from .models.category import Category
from .schemas import (
    QuizCreate,
    QuizRead,
    QuizUpdate,
    StudentCreate,
    StudentRead,
    CategoryCreate,
    CategoryRead,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="REGISTON API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return {
        "status": "ok",
        "project": "REGISTON"
    }


@app.get("/analytics")
def analytics(db: Session = Depends(get_db)):
    total_quizzes = db.query(Quiz).count()
    total_students = db.query(Student).count()
    avg_score = db.query(func.avg(Student.score)).scalar() or 0
    return {
        "students": total_students,
        "quizzes": total_quizzes,
        "avg_score": round(avg_score, 1)
    }


@app.get("/categories", response_model=list[CategoryRead])
def read_categories(db: Session = Depends(get_db)):
    return db.query(Category).order_by(Category.created_at.desc()).all()


@app.post("/categories", response_model=CategoryRead)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    existing = db.query(Category).filter(Category.name == category.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category already exists")
    new = Category(name=category.name, description=category.description)
    db.add(new)
    db.commit()
    db.refresh(new)
    return new


@app.get("/students", response_model=list[StudentRead])
def read_students(db: Session = Depends(get_db)):
    return db.query(Student).order_by(Student.registered_at.desc()).all()


@app.post("/students", response_model=StudentRead)
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    existing = db.query(Student).filter(Student.email == student.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Student with this email already exists")
    db_student = Student(**student.dict())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


@app.get("/quizzes", response_model=list[QuizRead])
def read_quizzes(category_id: int | None = None, db: Session = Depends(get_db)):
    q = db.query(Quiz)
    if category_id is not None:
        q = q.filter(Quiz.category_id == category_id)
    return q.all()


@app.post("/quizzes", response_model=QuizRead)
def create_quiz(quiz: QuizCreate, db: Session = Depends(get_db)):
    data = quiz.dict()
    cat_id = data.get('category_id')
    if cat_id is not None:
        cat = db.query(Category).filter(Category.id == cat_id).first()
        if not cat:
            raise HTTPException(status_code=400, detail="Category not found")
    db_quiz = Quiz(**data)
    db.add(db_quiz)
    db.commit()
    db.refresh(db_quiz)
    return db_quiz


@app.get("/categories/{category_id}/top-students", response_model=list[StudentRead])
def get_top_students_for_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return db.query(Student).order_by(Student.score.desc()).limit(10).all()


@app.get("/quizzes/{quiz_id}", response_model=QuizRead)
def read_quiz(quiz_id: int, db: Session = Depends(get_db)):
    db_quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not db_quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return db_quiz


@app.put("/quizzes/{quiz_id}", response_model=QuizRead)
def update_quiz(quiz_id: int, quiz: QuizUpdate, db: Session = Depends(get_db)):
    db_quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not db_quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    for field, value in quiz.dict(exclude_unset=True).items():
        setattr(db_quiz, field, value)
    db.commit()
    db.refresh(db_quiz)
    return db_quiz


@app.delete("/quizzes/{quiz_id}")
def delete_quiz(quiz_id: int, db: Session = Depends(get_db)):
    db_quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not db_quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    db.delete(db_quiz)
    db.commit()
    return {"detail": "Quiz deleted"}
