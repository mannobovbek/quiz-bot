from fastapi import Depends, FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy import func
from sqlalchemy.orm import Session
from pydantic import EmailStr
import random
from datetime import datetime
from io import BytesIO

from .database import Base, SessionLocal, engine
from .services.analytics import (
    get_dashboard_metrics,
    get_top_quizzes,
    get_difficult_questions,
    get_recent_attempts,
    get_student_stats,
)
from .services.leaderboard import (
    get_global_leaderboard,
    get_category_leaderboard,
    get_student_rank,
)
from .services.excel_handler import (
    import_excel_questions,
    export_attempts_to_excel,
    export_question_template_to_excel,
)
from .models.quiz import Quiz, QuizStatus
from .models.student import Student
from .models.category import Category
from .models.question import Question
from .models.answer import Answer
from .models.quiz_attempt import QuizAttempt
from .models.attempt_answer import AttemptAnswer
from .schemas import (
    QuizCreate,
    QuizRead,
    QuizUpdate,
    StudentCreate,
    StudentRead,
    CategoryCreate,
    CategoryRead,
    QuizSubmitRequest,
    QuizSubmitResponse,
    QuizCreateNew,
    QuizUpdateNew,
    QuizReadNew,
    QuizReadFull,
    QuestionCreate,
    QuestionRead,
    QuestionReadForStudent,
    AttemptAnswerSubmit,
    QuizAttemptRead,
    QuizAttemptDetailRead,
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


@app.post("/quiz-attempt/submit", response_model=QuizSubmitResponse)
def submit_quiz_attempt(payload: QuizSubmitRequest, db: Session = Depends(get_db)):
    quiz = db.query(Quiz).filter(Quiz.id == payload.quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    student = db.query(Student).filter(Student.email == payload.student_email).first()
    if not student:
        student = Student(name=payload.student_name, email=payload.student_email, score=0)
        db.add(student)
        db.commit()
        db.refresh(student)

    correct = int(payload.selected_option_id) == int(quiz.correct)
    if correct:
        student.score = (student.score or 0) + 1
        db.add(student)
        db.commit()
        db.refresh(student)

    return QuizSubmitResponse(
        quiz_id=payload.quiz_id,
        student_email=payload.student_email,
        correct=correct,
        score=int(student.score or 0),
    )


# ====================== NEW PROFESSIONAL QUIZ SYSTEM ======================

# =================== QUIZ CRUD ENDPOINTS (NEW) ===================

@app.post("/v2/quizzes", response_model=QuizReadNew)
def create_quiz_v2(quiz_data: QuizCreateNew, db: Session = Depends(get_db)):
    """Create a new quiz with questions and answers"""
    if quiz_data.category_id:
        cat = db.query(Category).filter(Category.id == quiz_data.category_id).first()
        if not cat:
            raise HTTPException(status_code=400, detail="Category not found")
    
    new_quiz = Quiz(
        title=quiz_data.title,
        description=quiz_data.description,
        category_id=quiz_data.category_id,
        time_limit=quiz_data.time_limit,
        shuffle_questions=quiz_data.shuffle_questions,
        shuffle_answers=quiz_data.shuffle_answers,
        show_result=quiz_data.show_result,
        status=QuizStatus.DRAFT,
    )
    db.add(new_quiz)
    db.commit()
    db.refresh(new_quiz)
    return new_quiz


@app.get("/v2/quizzes/{quiz_id}", response_model=QuizReadFull)
def get_quiz_v2(quiz_id: int, db: Session = Depends(get_db)):
    """Get full quiz with all questions (for admin)"""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    questions = db.query(Question).filter(Question.quiz_id == quiz_id).order_by(Question.order_number).all()
    return {
        **QuizReadNew.model_validate(quiz).model_dump(),
        "questions": [QuestionRead.model_validate(q).model_dump() for q in questions]
    }


@app.put("/v2/quizzes/{quiz_id}", response_model=QuizReadNew)
def update_quiz_v2(quiz_id: int, quiz_data: QuizUpdateNew, db: Session = Depends(get_db)):
    """Update quiz metadata"""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    for field, value in quiz_data.dict(exclude_unset=True).items():
        if value is not None:
            setattr(quiz, field, value)
    
    quiz.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(quiz)
    return quiz


@app.patch("/v2/quizzes/{quiz_id}/publish")
def publish_quiz(quiz_id: int, db: Session = Depends(get_db)):
    """Publish a quiz (change status from DRAFT to PUBLISHED)"""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    # Check if quiz has questions
    question_count = db.query(Question).filter(Question.quiz_id == quiz_id).count()
    if question_count == 0:
        raise HTTPException(status_code=400, detail="Quiz must have at least one question")
    
    quiz.status = QuizStatus.PUBLISHED
    quiz.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(quiz)
    return {"status": "published", "quiz_id": quiz_id}


@app.get("/v2/quizzes", response_model=list[QuizReadNew])
def list_quizzes_v2(category_id: int | None = None, status: str | None = None, db: Session = Depends(get_db)):
    """List quizzes with filtering"""
    q = db.query(Quiz)
    
    if category_id:
        q = q.filter(Quiz.category_id == category_id)
    
    if status:
        try:
            status_enum = QuizStatus(status)
            q = q.filter(Quiz.status == status_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid status")
    
    return q.order_by(Quiz.created_at.desc()).all()


# =================== QUESTION CRUD ENDPOINTS ===================

@app.post("/v2/quizzes/{quiz_id}/questions", response_model=QuestionRead)
def create_question(quiz_id: int, question_data: QuestionCreate, db: Session = Depends(get_db)):
    """Add a question to a quiz"""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    new_question = Question(
        quiz_id=quiz_id,
        text=question_data.text,
        image_url=question_data.image_url,
        points=question_data.points,
        order_number=question_data.order_number,
    )
    db.add(new_question)
    db.flush()
    
    # Add answers
    correct_count = sum(1 for a in question_data.answers if a.is_correct)
    if correct_count != 1:
        raise HTTPException(status_code=400, detail="Question must have exactly one correct answer")
    
    for answer_data in question_data.answers:
        new_answer = Answer(
            question_id=new_question.id,
            text=answer_data.text,
            is_correct=answer_data.is_correct,
        )
        db.add(new_answer)
    
    db.commit()
    db.refresh(new_question)
    
    # Load answers
    answers = db.query(Answer).filter(Answer.question_id == new_question.id).all()
    return {
        **QuestionRead.model_validate(new_question).model_dump(),
        "answers": [AnswerRead.model_validate(a).model_dump() for a in answers]
    }


@app.delete("/v2/questions/{question_id}")
def delete_question(question_id: int, db: Session = Depends(get_db)):
    """Delete a question and its answers"""
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    db.delete(question)
    db.commit()
    return {"detail": "Question deleted"}


# =================== QUIZ ATTEMPT ENDPOINTS ===================

@app.post("/v2/attempts/start")
def start_quiz_attempt(quiz_id: int, student_email: EmailStr, db: Session = Depends(get_db)):
    """Start a new quiz attempt"""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id, Quiz.status == QuizStatus.PUBLISHED).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found or not published")
    
    student = db.query(Student).filter(Student.email == student_email).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    attempt = QuizAttempt(
        student_id=student.id,
        quiz_id=quiz_id,
        started_at=datetime.utcnow(),
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    
    return {
        "attempt_id": attempt.id,
        "quiz_id": quiz_id,
        "started_at": attempt.started_at,
    }


@app.get("/v2/attempts/{attempt_id}/questions")
def get_attempt_questions(attempt_id: int, db: Session = Depends(get_db)):
    """Get questions for an attempt (with shuffling applied if enabled)"""
    attempt = db.query(QuizAttempt).filter(QuizAttempt.id == attempt_id).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")
    
    quiz = db.query(Quiz).filter(Quiz.id == attempt.quiz_id).first()
    questions = db.query(Question).filter(Question.quiz_id == attempt.quiz_id).order_by(Question.order_number).all()
    
    if not questions:
        raise HTTPException(status_code=400, detail="Quiz has no questions")
    
    # Apply shuffling if enabled
    if quiz.shuffle_questions:
        questions = random.sample(questions, len(questions))
    
    result = []
    for question in questions:
        answers = db.query(Answer).filter(Answer.question_id == question.id).all()
        
        if quiz.shuffle_answers:
            answers = random.sample(answers, len(answers))
        
        q_dict = {
            "id": question.id,
            "text": question.text,
            "image_url": question.image_url,
            "points": question.points,
            "answers": [
                {"id": a.id, "text": a.text}
                for a in answers
            ]
        }
        result.append(q_dict)
    
    return result


@app.post("/v2/attempts/{attempt_id}/answer")
def submit_answer(attempt_id: int, answer_data: AttemptAnswerSubmit, db: Session = Depends(get_db)):
    """Submit an answer to a question"""
    attempt = db.query(QuizAttempt).filter(QuizAttempt.id == attempt_id).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")
    
    question = db.query(Question).filter(Question.id == answer_data.question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    answer = db.query(Answer).filter(Answer.id == answer_data.selected_answer_id).first()
    if not answer:
        raise HTTPException(status_code=404, detail="Answer not found")
    
    # Check if answer already submitted
    existing = db.query(AttemptAnswer).filter(
        AttemptAnswer.attempt_id == attempt_id,
        AttemptAnswer.question_id == answer_data.question_id,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Answer already submitted for this question")
    
    is_correct = answer.is_correct
    
    attempt_answer = AttemptAnswer(
        attempt_id=attempt_id,
        question_id=answer_data.question_id,
        selected_answer_id=answer_data.selected_answer_id,
        is_correct=is_correct,
    )
    db.add(attempt_answer)
    
    # Update attempt stats
    if is_correct:
        attempt.correct_count += 1
    else:
        attempt.wrong_count += 1
    
    attempt.score += question.points if is_correct else 0
    
    db.commit()
    db.refresh(attempt)
    
    return {
        "is_correct": is_correct,
        "score": attempt.score,
        "correct_count": attempt.correct_count,
        "wrong_count": attempt.wrong_count,
    }


@app.post("/v2/attempts/{attempt_id}/finish")
def finish_attempt(attempt_id: int, db: Session = Depends(get_db)):
    """Finish a quiz attempt and calculate final score"""
    attempt = db.query(QuizAttempt).filter(QuizAttempt.id == attempt_id).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")
    
    if attempt.finished_at:
        raise HTTPException(status_code=400, detail="Attempt already finished")
    
    attempt.finished_at = datetime.utcnow()
    
    # Calculate duration
    duration = (attempt.finished_at - attempt.started_at).total_seconds()
    attempt.duration = int(duration)
    
    # Calculate total possible points
    total_questions = db.query(Question).filter(Question.quiz_id == attempt.quiz_id).count()
    total_possible_points = db.query(func.sum(Question.points)).filter(
        Question.quiz_id == attempt.quiz_id
    ).scalar() or total_questions
    
    attempt.percentage = (attempt.score / total_possible_points * 100) if total_possible_points > 0 else 0
    
    # Update student stats
    student = attempt.student
    student.attempts_count += 1
    student.last_attempt_date = datetime.utcnow()
    
    # Calculate average percentage
    all_attempts = db.query(QuizAttempt).filter(QuizAttempt.student_id == student.id).all()
    total_percentage = sum(a.percentage for a in all_attempts)
    student.avg_percentage = total_percentage / len(all_attempts) if all_attempts else 0
    
    db.commit()
    db.refresh(attempt)
    
    return {
        "attempt_id": attempt.id,
        "finished_at": attempt.finished_at,
        "score": attempt.score,
        "percentage": round(attempt.percentage, 2),
        "correct_count": attempt.correct_count,
        "wrong_count": attempt.wrong_count,
        "duration": attempt.duration,
    }


@app.get("/v2/attempts/{attempt_id}", response_model=QuizAttemptDetailRead)
def get_attempt_detail(attempt_id: int, db: Session = Depends(get_db)):
    """Get detailed information about an attempt (for admin review)"""
    attempt = db.query(QuizAttempt).filter(QuizAttempt.id == attempt_id).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")
    
    answers = db.query(AttemptAnswer).filter(AttemptAnswer.attempt_id == attempt_id).all()
    
    return {
        **QuizAttemptRead.model_validate(attempt).model_dump(),
        "answers": [
            {
                "id": a.id,
                "attempt_id": a.attempt_id,
                "question_id": a.question_id,
                "selected_answer_id": a.selected_answer_id,
                "is_correct": a.is_correct,
                "answered_at": a.answered_at,
            }
            for a in answers
        ]
    }


@app.get("/v2/students/{student_id}/attempts")
def get_student_attempts(student_id: int, db: Session = Depends(get_db)):
    """Get all attempts for a student"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    attempts = db.query(QuizAttempt).filter(QuizAttempt.student_id == student_id).order_by(
        QuizAttempt.started_at.desc()
    ).all()
    
    return [
        {
            "id": a.id,
            "quiz_id": a.quiz_id,
            "score": a.score,
            "percentage": round(a.percentage, 2),
            "started_at": a.started_at,
            "finished_at": a.finished_at,
        }
        for a in attempts
    ]


@app.delete("/v2/quizzes/{quiz_id}")
def delete_quiz_v2(quiz_id: int, db: Session = Depends(get_db)):
    """Delete a quiz and all related data"""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    db.delete(quiz)
    db.commit()
    return {"detail": "Quiz deleted"}


# ============================================================================
# PHASE 2: ANALYTICS & DASHBOARD ENDPOINTS
# ============================================================================

@app.get("/v2/admin/analytics")
def get_analytics(db: Session = Depends(get_db)):
    """
    Get dashboard analytics with key metrics.
    Returns: total_students, total_quizzes, today_submissions, average_score, etc.
    """
    metrics = get_dashboard_metrics(db)
    
    # Get top quiz and recent attempts
    top_quizzes = get_top_quizzes(db, limit=1)
    recent = get_recent_attempts(db, limit=5)
    
    return {
        **metrics,
        "top_quiz": top_quizzes["by_attempts"][0] if top_quizzes["by_attempts"] else None,
        "recent_attempts": recent["attempts"],
    }


@app.get("/v2/admin/top-quizzes")
def get_top_quizzes_endpoint(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get top quizzes by attempt count and average score.
    """
    return get_top_quizzes(db, limit=limit)


@app.get("/v2/admin/difficult-questions")
def get_difficult_endpoint(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get questions with lowest pass rates.
    Useful for identifying which questions need review.
    """
    try:
        return get_difficult_questions(db, limit=limit)
    except Exception as e:
        return {
            "difficult_questions": [],
            "error": "Could not calculate difficulty metrics"
        }


@app.get("/v2/admin/recent-attempts")
def get_recent_attempts_endpoint(
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    Get recent quiz submissions.
    """
    return get_recent_attempts(db, limit=limit)


@app.get("/v2/students/{student_id}/profile")
def get_student_profile(
    student_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed student profile with stats and attempt history.
    """
    stats = get_student_stats(db, student_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Get recent attempts
    attempts = (
        db.query(QuizAttempt)
        .filter(
            QuizAttempt.student_id == student_id,
            QuizAttempt.finished_at.isnot(None)
        )
        .order_by(QuizAttempt.finished_at.desc())
        .limit(10)
        .all()
    )
    
    recent_attempts = []
    for attempt in attempts:
        quiz = db.query(Quiz).filter(Quiz.id == attempt.quiz_id).first()
        recent_attempts.append({
            "attempt_id": attempt.id,
            "quiz_name": quiz.title if quiz else "Unknown",
            "quiz_id": attempt.quiz_id,
            "score": attempt.score,
            "percentage": round(attempt.percentage, 2) if attempt.percentage else 0,
            "duration_minutes": attempt.duration // 60 if attempt.duration else 0,
            "submitted_at": attempt.finished_at.isoformat() if attempt.finished_at else None,
        })
    
    stats["recent_attempts"] = recent_attempts
    return stats


@app.get("/v2/leaderboard")
def get_global_leaderboard_endpoint(
    limit: int = 10,
    offset: int = 0,
    period: str = "all",
    db: Session = Depends(get_db)
):
    """
    Get global leaderboard (top students by average score).
    Period: 'all', 'week', 'month'
    """
    if period not in ["all", "week", "month"]:
        raise HTTPException(status_code=400, detail="Period must be 'all', 'week', or 'month'")
    
    return get_global_leaderboard(db, limit=limit, offset=offset, period=period)


@app.get("/v2/leaderboard/category/{category_id}")
def get_category_leaderboard_endpoint(
    category_id: int,
    limit: int = 10,
    offset: int = 0,
    period: str = "all",
    db: Session = Depends(get_db)
):
    """
    Get leaderboard for a specific category.
    Period: 'all', 'week', 'month'
    """
    if period not in ["all", "week", "month"]:
        raise HTTPException(status_code=400, detail="Period must be 'all', 'week', or 'month'")
    
    return get_category_leaderboard(
        db,
        category_id=category_id,
        limit=limit,
        offset=offset,
        period=period
    )


@app.get("/v2/leaderboard/rank/{student_id}")
def get_student_rank_endpoint(
    student_id: int,
    db: Session = Depends(get_db)
):
    """
    Get student's rank and position in global leaderboard.
    """
    rank_info = get_student_rank(db, student_id)
    if not rank_info:
        raise HTTPException(status_code=404, detail="Student not found")
    
    return rank_info


# ============================================================================
# EXCEL IMPORT/EXPORT ENDPOINTS
# ============================================================================

@app.post("/v2/admin/import/excel")
def import_excel_file(
    file: UploadFile = File(...),
    quiz_name: str = "",
    quiz_description: str = "",
    category_id: int = None,
    db: Session = Depends(get_db)
):
    """
    Import questions from Excel file.
    File format: Savol | A | B | C | D | To'g'ri
    """
    if not quiz_name:
        raise HTTPException(status_code=400, detail="quiz_name is required")
    
    if file.content_type != "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        raise HTTPException(
            status_code=415,
            detail="File must be .xlsx (Excel format)"
        )
    
    try:
        content = file.file.read()
        result = import_excel_questions(
            db,
            content,
            quiz_name=quiz_name,
            quiz_description=quiz_description,
            category_id=category_id,
        )
        return result
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")


@app.get("/v2/admin/export/template")
def export_excel_template():
    """
    Download blank template for bulk question import.
    Use this as a starting point for preparing questions.
    """
    excel_file = export_question_template_to_excel()
    
    return StreamingResponse(
        iter([excel_file.getvalue()]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=question_template.xlsx"}
    )


@app.get("/v2/admin/export/attempts")
def export_attempts_file(
    start_date: str = None,
    end_date: str = None,
    quiz_id: int = None,
    category_id: int = None,
    student_id: int = None,
    db: Session = Depends(get_db)
):
    """
    Export quiz attempts to Excel file.
    Query params: start_date, end_date (YYYY-MM-DD), quiz_id, category_id, student_id
    """
    
    start_dt = None
    end_dt = None
    
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="start_date must be in YYYY-MM-DD format"
            )
    
    if end_date:
        try:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            end_dt = end_dt.replace(hour=23, minute=59, second=59)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="end_date must be in YYYY-MM-DD format"
            )
    
    try:
        excel_file = export_attempts_to_excel(
            db,
            start_date=start_dt,
            end_date=end_dt,
            quiz_id=quiz_id,
            category_id=category_id,
            student_id=student_id,
        )
        
        return StreamingResponse(
            iter([excel_file.getvalue()]),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=quiz_attempts_export.xlsx"}
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

