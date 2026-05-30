from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import Base, SessionLocal, engine
from .models.quiz import Quiz
from .schemas import QuizCreate, QuizRead, QuizUpdate

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
    return {
        "students": 1523,
        "quizzes": total_quizzes,
        "avg_score": 74
    }


@app.get("/quizzes", response_model=list[QuizRead])
def read_quizzes(db: Session = Depends(get_db)):
    return db.query(Quiz).all()


@app.post("/quizzes", response_model=QuizRead)
def create_quiz(quiz: QuizCreate, db: Session = Depends(get_db)):
    db_quiz = Quiz(**quiz.dict())
    db.add(db_quiz)
    db.commit()
    db.refresh(db_quiz)
    return db_quiz


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
