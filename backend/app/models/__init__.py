"""SQLAlchemy models package.

This file is required so that SQLAlchemy's declarative registry can reliably
import related models before relationship resolution.
"""

# Import models so relationships like relationship("Category") resolve.
from .category import Category  # noqa: F401
from .quiz import Quiz  # noqa: F401
from .question import Question  # noqa: F401
from .answer import Answer  # noqa: F401
from .quiz_attempt import QuizAttempt  # noqa: F401
from .attempt_answer import AttemptAnswer  # noqa: F401
from .student import Student  # noqa: F401

