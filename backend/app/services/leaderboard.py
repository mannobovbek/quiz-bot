"""
Leaderboard service for ranking students.
Calculates global and category-specific rankings.
"""

from datetime import datetime, timedelta
from sqlalchemy import func, and_
from sqlalchemy.orm import Session
from ..models.student import Student
from ..models.quiz import Quiz
from ..models.quiz_attempt import QuizAttempt


def get_global_leaderboard(db: Session, limit: int = 10, offset: int = 0, period: str = "all"):
    """
    Get global leaderboard (top students by average score).
    
    Args:
        db: Database session
        limit: Number of results
        offset: Pagination offset
        period: "all", "week", or "month"
    
    Returns: List of ranked students with scores
    """
    
    # Calculate date filter
    if period == "week":
        days = 7
    elif period == "month":
        days = 30
    else:  # "all"
        days = None
    
    start_date = (datetime.now() - timedelta(days=days)) if days else None
    
    # Query with ranking
    query = (
        db.query(
            Student.id,
            Student.name,
            func.avg(QuizAttempt.percentage).label("avg_score"),
            func.count(QuizAttempt.id).label("attempts"),
        )
        .outerjoin(QuizAttempt)
        .filter(QuizAttempt.finished_at.isnot(None))
    )
    
    if start_date:
        query = query.filter(QuizAttempt.finished_at >= start_date)
    
    results = (
        query.group_by(Student.id, Student.name)
        .having(func.count(QuizAttempt.id) > 0)
        .order_by(func.avg(QuizAttempt.percentage).desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    
    total_students = (
        db.query(func.count(Student.id.distinct()))
        .join(QuizAttempt)
        .filter(
            and_(
                QuizAttempt.finished_at.isnot(None),
                QuizAttempt.finished_at >= start_date if start_date else True
            )
        )
        .scalar() or 0
    )
    
    leaderboard = []
    for i, (student_id, name, avg_score, attempts) in enumerate(results):
        leaderboard.append({
            "rank": offset + i + 1,
            "student_id": student_id,
            "name": name,
            "average_score": round(avg_score, 2) if avg_score else 0,
            "attempts": attempts,
            "badges": get_student_badges(avg_score, attempts) if avg_score else [],
        })
    
    return {
        "period": period,
        "total_students": total_students,
        "leaderboard": leaderboard,
    }


def get_category_leaderboard(
    db: Session, category_id: int, limit: int = 10, offset: int = 0, period: str = "all"
):
    """
    Get leaderboard for specific category.
    
    Args:
        db: Database session
        category_id: Category ID
        limit: Number of results
        offset: Pagination offset
        period: "all", "week", or "month"
    
    Returns: List of ranked students in category
    """
    
    # Calculate date filter
    if period == "week":
        days = 7
    elif period == "month":
        days = 30
    else:  # "all"
        days = None
    
    start_date = (datetime.now() - timedelta(days=days)) if days else None
    
    # Query
    query = (
        db.query(
            Student.id,
            Student.name,
            func.avg(QuizAttempt.percentage).label("avg_score"),
            func.count(QuizAttempt.id).label("attempts"),
        )
        .outerjoin(QuizAttempt)
        .join(Quiz)
        .filter(
            and_(
                Quiz.category == category_id,
                QuizAttempt.finished_at.isnot(None)
            )
        )
    )
    
    if start_date:
        query = query.filter(QuizAttempt.finished_at >= start_date)
    
    results = (
        query.group_by(Student.id, Student.name)
        .having(func.count(QuizAttempt.id) > 0)
        .order_by(func.avg(QuizAttempt.percentage).desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    
    total_students = (
        db.query(func.count(Student.id.distinct()))
        .join(QuizAttempt)
        .join(Quiz)
        .filter(
            and_(
                Quiz.category == category_id,
                QuizAttempt.finished_at.isnot(None),
                QuizAttempt.finished_at >= start_date if start_date else True
            )
        )
        .scalar() or 0
    )
    
    leaderboard = []
    for i, (student_id, name, avg_score, attempts) in enumerate(results):
        leaderboard.append({
            "rank": offset + i + 1,
            "student_id": student_id,
            "name": name,
            "average_score": round(avg_score, 2) if avg_score else 0,
            "attempts": attempts,
            "badges": get_student_badges(avg_score, attempts) if avg_score else [],
        })
    
    return {
        "period": period,
        "category_id": category_id,
        "total_students": total_students,
        "leaderboard": leaderboard,
    }


def get_student_rank(db: Session, student_id: int):
    """
    Get student's global rank and stats.
    """
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        return None
    
    # Get student's average score
    student_avg = (
        db.query(func.avg(QuizAttempt.percentage))
        .filter(
            and_(
                QuizAttempt.student_id == student_id,
                QuizAttempt.finished_at.isnot(None)
            )
        )
        .scalar() or 0
    )
    
    if student_avg == 0:
        return {
            "student_id": student_id,
            "name": student.name,
            "average_score": 0,
            "rank": None,
            "total_students": 0,
            "percentile": 0,
        }
    
    # Count students with higher score
    rank = (
        db.query(func.count(Student.id.distinct()))
        .join(QuizAttempt)
        .filter(
            and_(
                QuizAttempt.finished_at.isnot(None),
                func.avg(QuizAttempt.percentage) > student_avg
            )
        )
        .scalar() or 0
    ) + 1
    
    # Total students with attempts
    total_students = (
        db.query(func.count(Student.id.distinct()))
        .join(QuizAttempt)
        .filter(QuizAttempt.finished_at.isnot(None))
        .scalar() or 0
    )
    
    percentile = (1 - (rank - 1) / max(total_students, 1)) * 100
    
    return {
        "student_id": student_id,
        "name": student.name,
        "average_score": round(student_avg, 2),
        "rank": rank,
        "total_students": total_students,
        "percentile": round(percentile, 1),
    }


def get_student_badges(avg_score, attempts):
    """
    Determine badges based on performance.
    """
    badges = []
    
    if avg_score >= 90:
        badges.append("top_performer")
    elif avg_score >= 75:
        badges.append("consistent")
    
    if attempts >= 50:
        badges.append("active_learner")
    elif attempts >= 20:
        badges.append("engaged")
    
    if avg_score >= 85 and attempts >= 10:
        badges.append("quick_learner")
    
    return badges
