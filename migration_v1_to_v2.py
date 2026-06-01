"""
Database Migration Script for Phase 1
This script migrates from the old quiz format to the new professional system.

Run this ONCE after updating the code:
python backend/migration_v1_to_v2.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.database import engine, SessionLocal
from app.models.quiz import Quiz, QuizStatus
from app.models.category import Category
from app.models.question import Question
from app.models.answer import Answer
from app.models.student import Student
from app.models.quiz_attempt import QuizAttempt
from app.models.attempt_answer import AttemptAnswer
from sqlalchemy import inspect
import sqlalchemy as sa


def create_tables():
    """Create all new tables"""
    print("📊 Creating database tables...")
    
    # Create all tables from Base metadata
    from app.database import Base
    Base.metadata.create_all(bind=engine)
    
    print("✅ Tables created successfully!")


def add_missing_columns():
    """Add missing columns to existing tables"""
    print("🔧 Adding missing columns...")
    
    db = SessionLocal()
    inspector = inspect(engine)
    
    # Check and add columns to quiz table
    quiz_columns = {col['name'] for col in inspector.get_columns('quizzes')}
    required_quiz_cols = {
        'title', 'description', 'time_limit', 'shuffle_questions',
        'shuffle_answers', 'show_result', 'status', 'created_at', 'updated_at'
    }
    
    with engine.begin() as connection:
        for col in required_quiz_cols:
            if col not in quiz_columns:
                print(f"  Adding column: quiz.{col}")
                
                if col == 'title':
                    connection.execute(sa.text(
                        "ALTER TABLE quizzes ADD COLUMN title VARCHAR"
                    ))
                elif col == 'description':
                    connection.execute(sa.text(
                        "ALTER TABLE quizzes ADD COLUMN description TEXT"
                    ))
                elif col == 'time_limit':
                    connection.execute(sa.text(
                        "ALTER TABLE quizzes ADD COLUMN time_limit INTEGER DEFAULT 0"
                    ))
                elif col == 'shuffle_questions':
                    connection.execute(sa.text(
                        "ALTER TABLE quizzes ADD COLUMN shuffle_questions BOOLEAN DEFAULT FALSE"
                    ))
                elif col == 'shuffle_answers':
                    connection.execute(sa.text(
                        "ALTER TABLE quizzes ADD COLUMN shuffle_answers BOOLEAN DEFAULT FALSE"
                    ))
                elif col == 'show_result':
                    connection.execute(sa.text(
                        "ALTER TABLE quizzes ADD COLUMN show_result BOOLEAN DEFAULT TRUE"
                    ))
                elif col == 'status':
                    connection.execute(sa.text(
                        "ALTER TABLE quizzes ADD COLUMN status VARCHAR DEFAULT 'draft'"
                    ))
                elif col == 'created_at':
                    connection.execute(sa.text(
                        "ALTER TABLE quizzes ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
                    ))
                elif col == 'updated_at':
                    connection.execute(sa.text(
                        "ALTER TABLE quizzes ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
                    ))
    
    # Check and add columns to students table
    student_columns = {col['name'] for col in inspector.get_columns('students')}
    required_student_cols = {'attempts_count', 'avg_percentage', 'last_attempt_date', 'updated_at'}
    
    with engine.begin() as connection:
        for col in required_student_cols:
            if col not in student_columns:
                print(f"  Adding column: student.{col}")
                
                if col == 'attempts_count':
                    connection.execute(sa.text(
                        "ALTER TABLE students ADD COLUMN attempts_count INTEGER DEFAULT 0"
                    ))
                elif col == 'avg_percentage':
                    connection.execute(sa.text(
                        "ALTER TABLE students ADD COLUMN avg_percentage FLOAT DEFAULT 0.0"
                    ))
                elif col == 'last_attempt_date':
                    connection.execute(sa.text(
                        "ALTER TABLE students ADD COLUMN last_attempt_date TIMESTAMP"
                    ))
                elif col == 'updated_at':
                    connection.execute(sa.text(
                        "ALTER TABLE students ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
                    ))
    
    print("✅ Columns added!")


def migrate_legacy_quizzes():
    """Migrate old quiz format to questions/answers format"""
    print("🔄 Migrating legacy quizzes...")
    
    db = SessionLocal()
    
    # Get all quizzes with legacy data (has 'question' field)
    legacy_quizzes = db.query(Quiz).filter(
        Quiz.question != None,
        Quiz.option1 != None
    ).all()
    
    if not legacy_quizzes:
        print("  No legacy quizzes to migrate")
        return
    
    print(f"  Found {len(legacy_quizzes)} legacy quizzes")
    
    for old_quiz in legacy_quizzes:
        try:
            # Create title from question if needed
            if not old_quiz.title:
                old_quiz.title = old_quiz.question[:100] or f"Quiz {old_quiz.id}"
            
            # Set status to published since it was in use
            if old_quiz.status is None:
                old_quiz.status = QuizStatus.PUBLISHED
            
            # Create question
            question = Question(
                quiz_id=old_quiz.id,
                text=old_quiz.question,
                points=1,
                order_number=1,
            )
            db.add(question)
            db.flush()
            
            # Create answers
            options = [
                (old_quiz.option1, old_quiz.correct == 1),
                (old_quiz.option2, old_quiz.correct == 2),
                (old_quiz.option3, old_quiz.correct == 3),
                (old_quiz.option4, old_quiz.correct == 4),
            ]
            
            for i, (option_text, is_correct) in enumerate(options, 1):
                if option_text:
                    answer = Answer(
                        question_id=question.id,
                        text=option_text,
                        is_correct=is_correct,
                    )
                    db.add(answer)
            
            print(f"  ✅ Migrated quiz: {old_quiz.title}")
            
        except Exception as e:
            print(f"  ❌ Error migrating quiz {old_quiz.id}: {e}")
    
    db.commit()
    db.close()
    print("✅ Legacy quizzes migrated!")


def main():
    print("\n" + "="*60)
    print("  REGISTON Database Migration v1 -> v2")
    print("="*60 + "\n")
    
    try:
        # Step 1: Create tables
        create_tables()
        
        # Step 2: Add missing columns
        add_missing_columns()
        
        # Step 3: Migrate legacy data
        migrate_legacy_quizzes()
        
        print("\n" + "="*60)
        print("  ✅ Migration completed successfully!")
        print("="*60 + "\n")
        print("Next steps:")
        print("1. Update bot: use main_v2.py instead of main.py")
        print("2. Update frontend to use new v2 API endpoints")
        print("3. Start creating quizzes with the new admin panel")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
