"""
Analytics service for dashboard metrics and statistics.

Calculates real-time metrics for admin dashboard.
"""

from datetime import datetime, timedelta
from sqlalchemy import func, and_, select
from sqlalchemy.orm import Session
from ..models.student import Student
from ..models.quiz import Quiz
from ..models.quiz_attempt import QuizAttempt
from ..models.attempt_answer import AttemptAnswer
from ..models.question import Question


def get_dashboard_metrics(db: Session):
    """
    Get key metrics for admin dashboard.
    Returns: total students, quizzes, today's submissions, average score
    """
    # Total students
    total_students = db.query(func.count(Student.id)).scalar() or 0
    
    # Total published quizzes
    total_quizzes = (
        db.query(func.count(Quiz.id))
        .filter(Quiz.status == "published")
        .scalar() or 0
    )
    
    # Today's submissions
    today = datetime.now().date()
    today_submissions = (
        db.query(func.count(QuizAttempt.id))
        .filter(
            and_(
                QuizAttempt.finished_at.isnot(None),
                func.date(QuizAttempt.started_at) == today
            )
        )
        .scalar() or 0
    )
    
    # Average score across all attempts
    avg_score = (
        db.query(func.avg(QuizAttempt.percentage))
        .filter(QuizAttempt.finished_at.isnot(None))
        .scalar() or 0
    )
    
    # Total attempts
    total_attempts = (
        db.query(func.count(QuizAttempt.id))
        .filter(QuizAttempt.finished_at.isnot(None))
        .scalar() or 0
    )
    
    # Completion rate (finished / started)
    started_attempts = (
        db.query(func.count(QuizAttempt.id)).scalar() or 0
    )
    completion_rate = (
        (total_attempts / started_attempts * 100) if started_attempts > 0 else 0
    )
    
    return {
        "total_students": total_students,
        "total_quizzes": total_quizzes,
        "today_submissions": today_submissions,
        "average_score": round(avg_score, 2),
        "total_attempts": total_attempts,
        "completion_rate": round(completion_rate, 1),
    }


def get_top_quizzes(db: Session, limit: int = 10):
    """
    Get top quizzes by attempt count and average score.
    Returns: by_attempts, by_score
    """
    # By attempts
    top_by_attempts = (
        db.query(
            Quiz.id,
            Quiz.title,
            func.count(QuizAttempt.id).label("attempts"),
            func.avg(QuizAttempt.percentage).label("avg_score")
        )
        .outerjoin(QuizAttempt)
        .filter(Quiz.status == "published")
        .group_by(Quiz.id)
        .order_by(func.count(QuizAttempt.id).desc())
        .limit(limit)
        .all()
    )
    
    # By score
    top_by_score = (
        db.query(
            Quiz.id,
            Quiz.title,
            func.count(QuizAttempt.id).label("attempts"),
            func.avg(QuizAttempt.percentage).label("avg_score")
        )
        .outerjoin(QuizAttempt)
        .filter(Quiz.status == "published")
        .group_by(Quiz.id)
        .having(func.count(QuizAttempt.id) > 0)
        .order_by(func.avg(QuizAttempt.percentage).desc())
        .limit(limit)
        .all()
    )
    
    return {
        "by_attempts": [
            {
                "rank": i + 1,
                "quiz_id": q[0],
                "quiz_name": q[1],
                "attempts": q[2],
                "avg_score": round(q[3], 2) if q[3] else 0,
            }
            for i, q in enumerate(top_by_attempts)
        ],
        "by_score": [
            {
                "rank": i + 1,
                "quiz_id": q[0],
                "quiz_name": q[1],
                "attempts": q[2],
                "avg_score": round(q[3], 2) if q[3] else 0,
            }
            for i, q in enumerate(top_by_score)
        ],
    }


def get_difficult_questions(db: Session, limit: int = 10):
    """
    Get questions with lowest pass rates.
    Returns: question_id, question_text, pass_rate, difficulty
    """
    # Get all attempt answers with question and quiz info
    results = (
        db.query(
            Question.id,
            Question.text,
            Quiz.title,
        )
        .join(Quiz)
        .distinct(Question.id)
        .all()
    )
    
    difficult_list = []
    
    for question_id, text, quiz_name in results:
        # Count attempts and correct answers for this question
        total_attempts = (
            db.query(func.count(AttemptAnswer.id))
            .filter(AttemptAnswer.question_id == question_id)
            .scalar() or 0
        )
        
        correct_attempts = (
            db.query(func.count(AttemptAnswer.id))
            .filter(
                AttemptAnswer.question_id == question_id,
                AttemptAnswer.is_correct == True
            )
            .scalar() or 0
        )
        
        if total_attempts > 0:
            pass_rate = (correct_attempts / total_attempts * 100)
            
            # Determine difficulty
            if pass_rate > 75:
                difficulty = "easy"
            elif pass_rate > 50:
                difficulty = "medium"
            else:
                difficulty = "hard"
            
            difficult_list.append({
                "question_id": question_id,
                "question_text": text,
                "quiz_name": quiz_name,
                "total_attempts": total_attempts,
                "correct_attempts": correct_attempts,
                "pass_rate": round(pass_rate, 2),
                "difficulty": difficulty,
            })
    
    # Sort by pass rate (lowest first) and limit
    difficult_list.sort(key=lambda x: x["pass_rate"])
    return {"difficult_questions": difficult_list[:limit]}


def get_recent_attempts(db: Session, limit: int = 20):
    """
    Get recent quiz attempts.
    Returns: latest submissions with student info
    """
    try:
        attempts = (
            db.query(
                QuizAttempt.id,
                Student.id,
                Student.name,
                Quiz.id,
                Quiz.title,
                QuizAttempt.score,
                QuizAttempt.percentage,
                QuizAttempt.duration,
                QuizAttempt.finished_at,
            )
            .outerjoin(Student, QuizAttempt.student_id == Student.id)
            .outerjoin(Quiz, QuizAttempt.quiz_id == Quiz.id)
            .filter(QuizAttempt.finished_at.isnot(None))
            .order_by(QuizAttempt.finished_at.desc())
            .limit(limit)
            .all()
        )
    except Exception:
        # If join fails, return empty
        attempts = []
    
    return {
        "attempts": [
            {
                "attempt_id": a[0],
                "student_id": a[1],
                "student_name": a[2],
                "quiz_id": a[3],
                "quiz_name": a[4],
                "score": a[5],
                "percentage": round(a[6], 2) if a[6] else 0,
                "duration_minutes": a[7] // 60 if a[7] else 0,
                "submitted_at": a[8].isoformat() if a[8] else None,
            }
            for a in attempts
        ]
    }


def get_student_stats(db: Session, student_id: int):
    """
    Get comprehensive stats for a student.
    Returns: total attempts, average score, best/worst scores, streak
    """
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        return None
    
    # All attempts for this student
    attempts = (
        db.query(QuizAttempt)
        .filter(
            and_(
                QuizAttempt.student_id == student_id,
                QuizAttempt.finished_at.isnot(None)
            )
        )
        .order_by(QuizAttempt.finished_at.desc())
        .all()
    )
    
    if not attempts:
        return {
            "student_id": student_id,
            "name": student.name,
            "email": student.email,
            "joined_date": (getattr(student, "created_at", None) or getattr(student, "registered_at", None) or getattr(student, "updated_at", None)).isoformat() if (getattr(student, "created_at", None) or getattr(student, "registered_at", None) or getattr(student, "updated_at", None)) else None,
            "total_attempts": 0,



            "average_percentage": 0,
            "best_score": 0,
            "worst_score": 0,
            "attempts_this_week": 0,
            "study_streak_days": 0,
            "categories_attempted": 0,
        }
    
    # Calculate stats
    percentages = [a.percentage for a in attempts if a.percentage is not None]
    avg_percentage = sum(percentages) / len(percentages) if percentages else 0
    best_score = max(percentages) if percentages else 0
    worst_score = min(percentages) if percentages else 0
    
    # This week
    week_ago = datetime.now() - timedelta(days=7)
    attempts_this_week = sum(
        1 for a in attempts if a.finished_at and a.finished_at > week_ago
    )
    
    # Study streak (consecutive days with attempts)
    study_streak = calculate_study_streak(attempts)
    
    # Categories attempted
    categories_set = set()
    for attempt in attempts:
        quiz = db.query(Quiz).filter(Quiz.id == attempt.quiz_id).first()
        if quiz and quiz.category:
            categories_set.add(quiz.category)
    
    return {
        "student_id": student_id,
        "name": student.name,
        "email": student.email,
            "joined_date": (getattr(student, "created_at", None) or getattr(student, "registered_at", None) or getattr(student, "updated_at", None)).isoformat() if (getattr(student, "created_at", None) or getattr(student, "registered_at", None) or getattr(student, "updated_at", None)) else None,

        "total_attempts": len(attempts),
        "average_percentage": round(avg_percentage, 2),
        "best_score": round(best_score, 2),
        "worst_score": round(worst_score, 2),
        "attempts_this_week": attempts_this_week,
        "study_streak_days": study_streak,
        "categories_attempted": len(categories_set),
    }


def calculate_study_streak(attempts):
    """
    Calculate consecutive days with quiz attempts.
    Assumes attempts are sorted by date descending.
    """
    if not attempts:
        return 0
    
    streak = 1
    current_date = attempts[0].finished_at.date() if attempts[0].finished_at else None
    
    if not current_date:
        return 0
    
    for attempt in attempts[1:]:
        attempt_date = attempt.finished_at.date() if attempt.finished_at else None
        if not attempt_date:
            continue
        
        if (current_date - attempt_date).days == 1:
            streak += 1
            current_date = attempt_date
        else:
            break
    
    return streak
