# REGISTON Platform - Phase 1 Implementation Guide

## 🚀 What's Implemented (Phase 1)

### ✅ Database Models

- **Quiz** - Enhanced with title, description, shuffling options, status (draft/published/archived)
- **Question** - Individual questions with points and image support
- **Answer** - Answer options with correct flag
- **QuizAttempt** - Track when students take quizzes
- **AttemptAnswer** - Store individual student answers
- **Student** - Enhanced tracking (attempts count, avg percentage, last attempt)

### ✅ Core Features

1. **Quiz Attempt System** - Professional tracking of quiz submissions
2. **Answer History** - All student answers stored with correctness
3. **Shuffle Questions** - Random question order each attempt
4. **Shuffle Answers** - Random answer order each question
5. **Complete Telegram Bot Flow** - Full quiz experience in bot

---

## 🔧 Installation & Setup

### Step 1: Run Migration

```bash
cd /Users/dil5hodbek/Documents/Vscode/Bots/registon-platform

# Activate venv if not already active
source venv/bin/activate

# Run migration
python migration_v1_to_v2.py
```

Expected output:

```
✅ Tables created successfully!
✅ Columns added!
✅ Legacy quizzes migrated!
✅ Migration completed successfully!
```

### Step 2: Update Backend Dependencies

```bash
cd backend

# Check if all imports work
python -c "from app.main import *; print('✅ Imports OK')"

# Or restart backend service
python -m uvicorn app.main:app --reload
```

### Step 3: Update Bot

Replace current bot with new version:

```bash
# Backup old bot
cp bot/main.py bot/main_legacy.py

# Use new bot
cp bot/main_v2.py bot/main.py

# Or configure docker-compose to use main_v2.py
```

### Step 4: Restart Services

```bash
docker-compose down
docker-compose up --build
```

---

## 📡 API Endpoints (Phase 1)

### Quiz Management (New V2 API)

#### Create Quiz

```bash
POST /v2/quizzes
Content-Type: application/json

{
  "title": "Matematika Testi",
  "description": "Asosiy matematika bo'limining testi",
  "category_id": 1,
  "time_limit": 1800,
  "shuffle_questions": true,
  "shuffle_answers": true,
  "show_result": true
}
```

#### Add Question to Quiz

```bash
POST /v2/quizzes/{quiz_id}/questions
Content-Type: application/json

{
  "text": "2 + 2 = ?",
  "image_url": null,
  "points": 1,
  "order_number": 1,
  "answers": [
    {"text": "3", "is_correct": false},
    {"text": "4", "is_correct": true},
    {"text": "5", "is_correct": false},
    {"text": "6", "is_correct": false}
  ]
}
```

#### Publish Quiz (Make Available)

```bash
PATCH /v2/quizzes/{quiz_id}/publish

Response:
{
  "status": "published",
  "quiz_id": 1
}
```

#### List Quizzes

```bash
GET /v2/quizzes?category_id=1&status=published

Response:
[
  {
    "id": 1,
    "title": "Matematika Testi",
    "description": "...",
    "status": "published",
    "shuffle_questions": true,
    "shuffle_answers": true,
    "created_at": "2025-06-01T10:00:00",
    "updated_at": "2025-06-01T10:00:00"
  }
]
```

### Quiz Attempts (Student Taking Quiz)

#### Start Attempt

```bash
POST /v2/attempts/start

{
  "quiz_id": 1,
  "student_email": "ali@gmail.com"
}

Response:
{
  "attempt_id": 5,
  "quiz_id": 1,
  "started_at": "2025-06-01T10:30:00"
}
```

#### Get Questions (With Shuffling)

```bash
GET /v2/attempts/{attempt_id}/questions

Response:
[
  {
    "id": 1,
    "text": "2 + 2 = ?",
    "image_url": null,
    "points": 1,
    "answers": [
      {"id": 3, "text": "5"},
      {"id": 2, "text": "4"},
      {"id": 4, "text": "6"},
      {"id": 1, "text": "3"}
    ]
  }
]

Note: Order is randomized if shuffle_answers=true
```

#### Submit Answer

```bash
POST /v2/attempts/{attempt_id}/answer

{
  "question_id": 1,
  "selected_answer_id": 2
}

Response:
{
  "is_correct": true,
  "score": 1,
  "correct_count": 1,
  "wrong_count": 0
}
```

#### Finish Attempt (Get Results)

```bash
POST /v2/attempts/{attempt_id}/finish

Response:
{
  "attempt_id": 5,
  "finished_at": "2025-06-01T10:45:00",
  "score": 8,
  "percentage": 80.0,
  "correct_count": 8,
  "wrong_count": 2,
  "duration": 900
}
```

#### Get Attempt Details (Admin Review)

```bash
GET /v2/attempts/{attempt_id}

Response:
{
  "id": 5,
  "student_id": 2,
  "quiz_id": 1,
  "score": 8,
  "percentage": 80.0,
  "correct_count": 8,
  "wrong_count": 2,
  "duration": 900,
  "started_at": "2025-06-01T10:30:00",
  "finished_at": "2025-06-01T10:45:00",
  "answers": [
    {
      "id": 1,
      "attempt_id": 5,
      "question_id": 1,
      "selected_answer_id": 2,
      "is_correct": true,
      "answered_at": "2025-06-01T10:31:00"
    }
  ]
}
```

#### Get Student's All Attempts

```bash
GET /v2/students/{student_id}/attempts

Response:
[
  {
    "id": 5,
    "quiz_id": 1,
    "score": 8,
    "percentage": 80.0,
    "started_at": "2025-06-01T10:30:00",
    "finished_at": "2025-06-01T10:45:00"
  }
]
```

---

## 🤖 Telegram Bot Flow

### User Journey

```
/start
  ↓
Enter email (Ali ali@gmail.com)
  ↓
Select category (📖 Kategoriya)
  ↓
Select quiz (📝 Quiz nomi)
  ↓
Answer questions (1/10)
  ↓
Quiz complete (Results shown)
  ↓
Back to category selection
```

### Features

- ✅ Shuffle questions each attempt
- ✅ Shuffle answers per question
- ✅ Real-time scoring feedback
- ✅ Progress indicator (1/10)
- ✅ Final results with percentage
- ✅ Multiple quizzes in one session

---

## 📊 Data Flow Example

### Create & Take a Quiz

**Step 1: Admin creates quiz**

```
POST /v2/quizzes → Quiz created in DRAFT
POST /v2/quizzes/1/questions → Question 1 added
POST /v2/quizzes/1/questions → Question 2 added
PATCH /v2/quizzes/1/publish → Quiz PUBLISHED
```

**Step 2: Student takes quiz**

```
POST /v2/attempts/start → Attempt #5 created
GET /v2/attempts/5/questions → Questions with shuffled answers
POST /v2/attempts/5/answer → Answer submitted, score updated
POST /v2/attempts/5/answer → Answer submitted, score updated
...
POST /v2/attempts/5/finish → Attempt finished, percentage calculated
```

**Step 3: Admin reviews results**

```
GET /v2/attempts/5 → Full attempt details with all answers
GET /v2/students/2/attempts → All student's attempts
```

---

## 🔍 Testing

### Test with cURL

#### Create Quiz

```bash
curl -X POST "http://127.0.0.1:8000/v2/quizzes" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Quiz",
    "description": "Test Description",
    "shuffle_questions": true,
    "shuffle_answers": true
  }'
```

#### Get Quiz

```bash
curl "http://127.0.0.1:8000/v2/quizzes/1"
```

#### Start Attempt

```bash
curl -X POST "http://127.0.0.1:8000/v2/attempts/start" \
  -H "Content-Type: application/json" \
  -d '{
    "quiz_id": 1,
    "student_email": "test@example.com"
  }'
```

---

## 📝 Next Steps (Phase 2 & 3)

### Phase 2: Analytics & Features

- [ ] Analytics dashboard with stats
- [ ] Student profile with history
- [ ] Leaderboard (top 10, by category)
- [ ] Excel import for bulk questions
- [ ] Excel export of results

### Phase 3: Advanced

- [ ] Role-based access (Admin, Teacher, Moderator)
- [ ] Teacher-specific dashboards
- [ ] Advanced analytics graphs
- [ ] Quiz difficulty tracking
- [ ] Student study recommendations

---

## 🐛 Troubleshooting

### Migration fails

```bash
# Check database connection
python -c "from app.database import engine; print(engine.url)"

# Check existing tables
sqlite3 test.db ".tables"
```

### Bot doesn't respond

- Check BOT_TOKEN in config.py
- Verify CHANNEL_ID is correct
- Check API_BASE points to running backend
- View bot logs: `docker logs registon-bot`

### API returns 404

- Ensure quiz is PUBLISHED (not DRAFT)
- Check quiz has questions
- Verify student email exists

---

## 📚 Database Schema

```
quizzes
├── id (PK)
├── title
├── description
├── category_id (FK)
├── time_limit
├── shuffle_questions
├── shuffle_answers
├── show_result
├── status (draft/published/archived)
├── created_at
└── updated_at

questions
├── id (PK)
├── quiz_id (FK)
├── text
├── image_url
├── points
├── order_number
├── created_at
└── updated_at

answers
├── id (PK)
├── question_id (FK)
├── text
├── is_correct
├── created_at
└── updated_at

quiz_attempts
├── id (PK)
├── student_id (FK)
├── quiz_id (FK)
├── started_at
├── finished_at
├── score
├── percentage
├── correct_count
├── wrong_count
├── duration

attempt_answers
├── id (PK)
├── attempt_id (FK)
├── question_id (FK)
├── selected_answer_id (FK)
├── is_correct
└── answered_at

students
├── id (PK)
├── name
├── email
├── score
├── attempts_count
├── avg_percentage
├── last_attempt_date
├── registered_at
└── updated_at
```

---

## 💡 Key Improvements Over Legacy

| Feature          | Old          | New                         |
| ---------------- | ------------ | --------------------------- |
| Questions        | Single Q & A | Multiple questions per quiz |
| Shuffling        | No           | Yes (questions + answers)   |
| Attempt Tracking | Basic score  | Full history + metadata     |
| Answer History   | None         | Complete tracking           |
| Quiz Status      | N/A          | Draft/Published/Archived    |
| Admin Controls   | Basic        | Rich metadata support       |
| Student Profile  | Minimal      | Detailed with stats         |
| Time Tracking    | No           | Full timing support         |

---

## ✨ What Makes This Professional

1. **Production-Ready Database** - Proper relationships, cascading deletes
2. **Audit Trail** - When each attempt was made, how long it took
3. **Anti-Cheating** - Shuffled questions & answers
4. **Analytics Ready** - All data for future dashboards
5. **Scalable API** - Versioned endpoints (v1 legacy, v2 new)
6. **User-Friendly Bot** - Smooth quiz flow in Telegram
7. **Admin Controls** - Quiz lifecycle management

---

**Created:** June 1, 2025  
**Status:** Phase 1 Complete ✅  
**Next:** Phase 2 (Analytics & Advanced Features)
