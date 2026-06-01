"""
Sample data for testing Phase 1
Run this to populate database with test quizzes and questions
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.database import SessionLocal
from app.models.category import Category
from app.models.quiz import Quiz, QuizStatus
from app.models.question import Question
from app.models.answer import Answer
from app.models.student import Student
from datetime import datetime


def create_sample_data():
    """Create sample data for testing"""
    db = SessionLocal()
    
    print("📊 Creating sample data...\n")
    
    try:
        # Clear existing test data
        db.query(Answer).delete()
        db.query(Question).delete()
        db.query(Quiz).filter(Quiz.title.like('%Test%')).delete()
        db.query(Category).filter(Category.name.like('%Matematika%')).delete()
        db.query(Student).filter(Student.email.like('%test%')).delete()
        db.commit()
        
        # Create categories
        print("✓ Creating categories...")
        math_cat = Category(
            name="Matematika",
            description="Asosiy matematika bo'limining savollar"
        )
        english_cat = Category(
            name="Ingliz Tili",
            description="Ingliz tilining asosiy leksikasi va grammatikasi"
        )
        db.add(math_cat)
        db.add(english_cat)
        db.commit()
        
        # Create test students
        print("✓ Creating test students...")
        student1 = Student(
            name="Ali Valiyev",
            email="ali@test.com",
            score=85,
            attempts_count=5,
            avg_percentage=82.5,
        )
        student2 = Student(
            name="Vali Aliyev",
            email="vali@test.com",
            score=90,
            attempts_count=3,
            avg_percentage=88.0,
        )
        db.add(student1)
        db.add(student2)
        db.commit()
        
        # Create math quiz
        print("✓ Creating Matematika Quiz...")
        math_quiz = Quiz(
            title="Matematika Testi",
            description="Asosiy matematika bo'limining testi",
            category_id=math_cat.id,
            time_limit=1800,
            shuffle_questions=True,
            shuffle_answers=True,
            show_result=True,
            status=QuizStatus.PUBLISHED,
        )
        db.add(math_quiz)
        db.commit()
        
        # Add math questions
        math_questions = [
            {
                "text": "2 + 2 = ?",
                "options": [
                    {"text": "3", "correct": False},
                    {"text": "4", "correct": True},
                    {"text": "5", "correct": False},
                    {"text": "6", "correct": False},
                ]
            },
            {
                "text": "5 × 6 = ?",
                "options": [
                    {"text": "25", "correct": False},
                    {"text": "30", "correct": True},
                    {"text": "35", "correct": False},
                    {"text": "40", "correct": False},
                ]
            },
            {
                "text": "√16 = ?",
                "options": [
                    {"text": "2", "correct": False},
                    {"text": "3", "correct": False},
                    {"text": "4", "correct": True},
                    {"text": "5", "correct": False},
                ]
            },
            {
                "text": "12 ÷ 3 = ?",
                "options": [
                    {"text": "3", "correct": False},
                    {"text": "4", "correct": True},
                    {"text": "5", "correct": False},
                    {"text": "6", "correct": False},
                ]
            },
        ]
        
        for i, q_data in enumerate(math_questions, 1):
            question = Question(
                quiz_id=math_quiz.id,
                text=q_data["text"],
                points=1,
                order_number=i,
            )
            db.add(question)
            db.flush()
            
            for opt in q_data["options"]:
                answer = Answer(
                    question_id=question.id,
                    text=opt["text"],
                    is_correct=opt["correct"],
                )
                db.add(answer)
        
        db.commit()
        print(f"  Added {len(math_questions)} math questions")
        
        # Create English quiz
        print("✓ Creating Ingliz Tili Quiz...")
        english_quiz = Quiz(
            title="English Vocabulary Test",
            description="Ingliz tilining asosiy leksikasi",
            category_id=english_cat.id,
            time_limit=1200,
            shuffle_questions=True,
            shuffle_answers=True,
            show_result=True,
            status=QuizStatus.PUBLISHED,
        )
        db.add(english_quiz)
        db.commit()
        
        # Add English questions
        english_questions = [
            {
                "text": "What is the opposite of 'hot'?",
                "options": [
                    {"text": "warm", "correct": False},
                    {"text": "cold", "correct": True},
                    {"text": "cool", "correct": False},
                    {"text": "freezing", "correct": False},
                ]
            },
            {
                "text": "Choose the correct spelling:",
                "options": [
                    {"text": "recieve", "correct": False},
                    {"text": "receive", "correct": True},
                    {"text": "recive", "correct": False},
                    {"text": "recieve", "correct": False},
                ]
            },
            {
                "text": "She _____ to the store yesterday.",
                "options": [
                    {"text": "go", "correct": False},
                    {"text": "goes", "correct": False},
                    {"text": "went", "correct": True},
                    {"text": "going", "correct": False},
                ]
            },
        ]
        
        for i, q_data in enumerate(english_questions, 1):
            question = Question(
                quiz_id=english_quiz.id,
                text=q_data["text"],
                points=1,
                order_number=i,
            )
            db.add(question)
            db.flush()
            
            for opt in q_data["options"]:
                answer = Answer(
                    question_id=question.id,
                    text=opt["text"],
                    is_correct=opt["correct"],
                )
                db.add(answer)
        
        db.commit()
        print(f"  Added {len(english_questions)} English questions")
        
        # Create a draft quiz (not published)
        print("✓ Creating Draft Quiz...")
        draft_quiz = Quiz(
            title="Advanced Mathematics",
            description="Foydalanish uchun tayyor bo'lmagan",
            category_id=math_cat.id,
            status=QuizStatus.DRAFT,
        )
        db.add(draft_quiz)
        db.commit()
        print("  (This quiz won't appear until published)")
        
        print("\n✅ Sample data created successfully!\n")
        print("📊 Summary:")
        print(f"  Categories: 2")
        print(f"  Published Quizzes: 2")
        print(f"  Total Questions: {len(math_questions) + len(english_questions)}")
        print(f"  Test Students: 2")
        print("\n🤖 Try with Telegram bot:")
        print("  1. /start")
        print("  2. Enter: Ali ali@test.com")
        print("  3. Select 'Matematika'")
        print("  4. Select 'Matematika Testi'")
        print("  5. Answer questions!")
        print("\n📡 Or test API directly:")
        print("  GET http://127.0.0.1:8000/v2/quizzes")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_sample_data()
