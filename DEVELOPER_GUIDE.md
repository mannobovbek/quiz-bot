# REGISTON Platform - Developer Quick Reference

## 🚀 Quick Start (5 minutes)

### 1. Setup Database

```bash
cd /Users/dil5hodbek/Documents/Vscode/Bots/registon-platform

# Run migration
python migration_v1_to_v2.py

# Create sample data (optional)
python create_sample_data.py
```

### 2. Start Services

```bash
# Option A: Docker (recommended)
docker-compose down
docker-compose up --build

# Option B: Manual
cd backend && python -m uvicorn app.main:app --reload
cd bot && python main_v2.py
```

### 3. Test Quiz Flow

- Go to Telegram, message bot `/start`
- Enter email: `ali@test.com`
- Select category → quiz → answer questions

---

## 📡 API Endpoints at a Glance

### Create Quiz (Admin)

```bash
POST /v2/quizzes
{
  "title": "Quiz Name",
  "shuffle_questions": true,
  "shuffle_answers": true,
  "category_id": 1
}
→ Returns: quiz_id
```

### Add Question

```bash
POST /v2/quizzes/{quiz_id}/questions
{
  "text": "Question?",
  "points": 1,
  "order_number": 1,
  "answers": [
    {"text": "Wrong", "is_correct": false},
    {"text": "Correct", "is_correct": true}
  ]
}
```

### Publish Quiz

```bash
PATCH /v2/quizzes/{quiz_id}/publish
→ Returns: published status
```

### Student Takes Quiz

```bash
# 1. Start
POST /v2/attempts/start
{"quiz_id": 1, "student_email": "ali@gmail.com"}
→ Returns: attempt_id

# 2. Get questions (shuffled)
GET /v2/attempts/{attempt_id}/questions

# 3. Submit answer
POST /v2/attempts/{attempt_id}/answer
{"question_id": 1, "selected_answer_id": 2}

# 4. Finish
POST /v2/attempts/{attempt_id}/finish
→ Returns: score, percentage
```

### Review (Admin)

```bash
# Student's attempt details
GET /v2/attempts/{attempt_id}

# All student attempts
GET /v2/students/{student_id}/attempts
```

---

## 🗄️ Database Quick Reference

### Core Tables

- `quizzes` - Quiz metadata
- `questions` - Questions (multiple per quiz)
- `answers` - Answer options (2+ per question)
- `quiz_attempts` - Student quiz sessions
- `attempt_answers` - Individual answers submitted
- `students` - Student info + stats
- `categories` - Quiz categories

### Key Fields

```
quizzes:
  ├─ status: "draft" | "published" | "archived"
  ├─ shuffle_questions: true/false
  ├─ shuffle_answers: true/false
  └─ time_limit: seconds (0 = no limit)

quiz_attempts:
  ├─ score: points
  ├─ percentage: 0-100
  ├─ duration: seconds
  └─ started_at, finished_at

attempt_answers:
  ├─ is_correct: true/false
  └─ answered_at: timestamp
```

---

## 🔧 Common Tasks

### Create a Quiz Programmatically

```python
import requests

# 1. Create quiz
r = requests.post('http://localhost:8000/v2/quizzes', json={
    'title': 'My Quiz',
    'shuffle_questions': True,
    'shuffle_answers': True,
    'category_id': 1
})
quiz_id = r.json()['id']

# 2. Add question
requests.post(f'http://localhost:8000/v2/quizzes/{quiz_id}/questions', json={
    'text': '2 + 2 = ?',
    'points': 1,
    'order_number': 1,
    'answers': [
        {'text': '4', 'is_correct': True},
        {'text': '3', 'is_correct': False},
        {'text': '5', 'is_correct': False},
    ]
})

# 3. Publish
requests.patch(f'http://localhost:8000/v2/quizzes/{quiz_id}/publish')
```

### Check Quiz Results

```python
# Get attempt details
r = requests.get('http://localhost:8000/v2/attempts/5')
data = r.json()
print(f"Score: {data['score']}/{data['total_points']}")
print(f"Percentage: {data['percentage']}%")
print(f"Duration: {data['duration']} seconds")
print(f"Answers: {data['answers']}")  # All submitted answers
```

### Export Student Performance

```python
# Get all attempts for a student
r = requests.get('http://localhost:8000/v2/students/2/attempts')
attempts = r.json()

for attempt in attempts:
    print(f"{attempt['quiz_id']}: {attempt['percentage']}%")
```

---

## 🧪 Testing Tips

### Test Shuffling

```python
# Get questions twice, should be different order
q1 = requests.get('http://localhost:8000/v2/attempts/1/questions').json()
q2 = requests.get('http://localhost:8000/v2/attempts/2/questions').json()

# Check if answer order differs
print(q1[0]['answers'])
print(q2[0]['answers'])
```

### Test Score Calculation

```python
# Submit correct answer
r = requests.post(f'http://localhost:8000/v2/attempts/1/answer', json={
    'question_id': 1,
    'selected_answer_id': 1  # Correct
})
print(r.json())  # {is_correct: true, score: 1, ...}

# Wrong answer
r = requests.post(f'http://localhost:8000/v2/attempts/1/answer', json={
    'question_id': 2,
    'selected_answer_id': 5  # Wrong
})
print(r.json())  # {is_correct: false, score: 1, ...}
```

---

## 📚 File Structure

```
registon-platform/
├── backend/
│   └── app/
│       ├── main.py (40+ v2 endpoints)
│       ├── schemas.py (comprehensive models)
│       └── models/
│           ├── quiz.py (with QuizStatus enum)
│           ├── question.py (NEW)
│           ├── answer.py (NEW)
│           ├── quiz_attempt.py (NEW)
│           ├── attempt_answer.py (NEW)
│           ├── student.py (enhanced)
│           └── category.py
├── bot/
│   ├── main.py (legacy)
│   ├── main_v2.py (NEW - professional)
│   └── config.py
├── migration_v1_to_v2.py (run once)
├── create_sample_data.py (optional)
└── PHASE1_GUIDE.md (detailed docs)
```

---

## 🐛 Troubleshooting

### Port 8000 already in use

```bash
lsof -i :8000
kill -9 <PID>
```

### Database locked

```bash
# SQLite locks - close other connections
# Or use: sqlite3 test.db "VACUUM;"
```

### Bot not responding

```bash
# Check config.py has correct BOT_TOKEN
# Check API_BASE points to running backend
# Docker logs: docker logs registon-bot
```

### Quiz has no questions error

```bash
# You must add at least one question before publishing
# Use: POST /v2/quizzes/{id}/questions
```

---

## 🎯 Next Steps

1. **Phase 2** - See `TODO.md` for analytics features
2. **Phase 3** - Role-based access control
3. **Questions?** - Check `PHASE1_GUIDE.md` for full docs

---

## 🔗 Useful Links

- API Docs: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- Phase 1 Guide: `PHASE1_GUIDE.md`
- Implementation: `PHASE1_GUIDE.md`

---

**Version:** 1.0 Phase 1  
**Updated:** June 1, 2025  
**Status:** ✅ Ready for Production Use
