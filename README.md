# REGISTON IMTIHON MARKAZI

🏛️ **Professional Full-Stack Quiz Platform for Telegram**

Full Stack Quiz Platform with advanced features for education and training.

## ✨ Features

### Phase 1 ✅ (COMPLETE)

- ✅ **Professional Quiz System** - Title, description, categories, metadata
- ✅ **Questions & Answers** - Multiple questions per quiz, rich formatting
- ✅ **Quiz Attempts Tracking** - Comprehensive audit trail of all attempts
- ✅ **Answer History** - Full record of each student's answers
- ✅ **Shuffle Questions** - Random question order per attempt (anti-cheating)
- ✅ **Shuffle Answers** - Random answer order per question
- ✅ **Quiz Status Lifecycle** - Draft → Published → Archived workflow
- ✅ **Complete Telegram Bot** - Full quiz experience without leaving Telegram
- ✅ **Instant Feedback** - Real-time scoring and results
- ✅ **Performance Tracking** - Student statistics and analytics data

### Phase 2 (In Progress)

- 📊 Analytics Dashboard with key metrics
- 👤 Student profiles with history
- 🏆 Leaderboard (global and by category)
- 📥 Excel import for bulk questions
- 📤 Results export as XLSX

### Phase 3 (Planned)

- 👥 Role-based access (Admin, Teacher, Moderator)
- 📈 Advanced analytics and graphs
- 🎖️ Achievements and badges
- 📧 Email notifications

## 🛠️ Tech Stack

- **Bot:** Aiogram 3 (Async Telegram)
- **Backend:** FastAPI + SQLAlchemy
- **Frontend:** React + Vite + Tailwind
- **Database:** PostgreSQL (Production) / SQLite (Dev)
- **Deploy:** Docker Compose

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Docker & Docker Compose
- Telegram Bot Token

### Installation

```bash
# Clone and setup
cd /Users/dil5hodbek/Documents/Vscode/Bots/registon-platform

# Run database migration (Phase 1)
python migration_v1_to_v2.py

# Create sample data (optional)
python create_sample_data.py

# Start all services
docker-compose up --build
```

### Telegram Bot

1. Message your bot `/start`
2. Enter your name and email
3. Select category → quiz
4. Answer questions with shuffled options
5. Get instant results!

### API Documentation

```
Swagger UI: http://localhost:8000/docs
ReDoc: http://localhost:8000/redoc
```

## 📡 API Overview

### Create Quiz (Admin)

```bash
POST /v2/quizzes
{
  "title": "Matematika",
  "shuffle_questions": true,
  "shuffle_answers": true,
  "category_id": 1
}
```

### Add Questions

```bash
POST /v2/quizzes/{quiz_id}/questions
{
  "text": "2 + 2 = ?",
  "points": 1,
  "answers": [
    {"text": "4", "is_correct": true},
    {"text": "3", "is_correct": false}
  ]
}
```

### Student Takes Quiz

```bash
# Start attempt
POST /v2/attempts/start
{"quiz_id": 1, "student_email": "ali@gmail.com"}

# Get questions (auto-shuffled)
GET /v2/attempts/{attempt_id}/questions

# Submit answer
POST /v2/attempts/{attempt_id}/answer
{"question_id": 1, "selected_answer_id": 2}

# Finish and get results
POST /v2/attempts/{attempt_id}/finish
```

### Review Results (Admin)

```bash
# Attempt details with all answers
GET /v2/attempts/{attempt_id}

# Student's all attempts
GET /v2/students/{student_id}/attempts
```

## 📚 Documentation

- **[PHASE1_GUIDE.md](PHASE1_GUIDE.md)** - Complete Phase 1 implementation (detailed API reference, database schema, testing guide)
- **[DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)** - Quick reference for developers (endpoints, common tasks, troubleshooting)
- **[TODO.md](TODO.md)** - Roadmap for Phase 2 & 3
- **API Docs:** `http://localhost:8000/docs` (after starting backend)

## 🔧 Project Structure

```
registon-platform/
├── backend/
│   └── app/
│       ├── main.py (40+ v2 API endpoints)
│       ├── database.py
│       ├── schemas.py (comprehensive models)
│       └── models/
│           ├── quiz.py (enhanced with metadata)
│           ├── question.py (new)
│           ├── answer.py (new)
│           ├── quiz_attempt.py (new)
│           ├── attempt_answer.py (new)
│           ├── student.py (enhanced)
│           └── category.py
├── bot/
│   ├── main.py (legacy version)
│   ├── main_v2.py (new professional bot)
│   └── config.py
├── webapp/
│   └── src/
│       ├── App.jsx
│       ├── pages/
│       │   ├── Dashboard.jsx
│       │   └── CreateQuiz.jsx
│       └── ...
├── migration_v1_to_v2.py (database migration)
├── create_sample_data.py (sample quizzes for testing)
├── docker-compose.yml
└── README.md
```

## 🎯 Key Improvements (Phase 1)

| Feature           | Before      | After                           |
| ----------------- | ----------- | ------------------------------- |
| Quiz Structure    | Single Q&A  | Multiple questions per quiz     |
| Shuffling         | ❌ No       | ✅ Questions & answers          |
| Tracking          | Basic score | Complete audit trail            |
| Answer History    | ❌ None     | ✅ Full history with timestamps |
| Status Management | ❌ No       | ✅ Draft/Published/Archived     |
| Admin Controls    | Limited     | Rich metadata + permissions     |
| Student Data      | Minimal     | Detailed performance metrics    |
| Time Tracking     | ❌ No       | ✅ Duration & scheduling        |

## 🚀 Usage Examples

### Create a Quiz via API

```bash
# 1. Create quiz
QUIZ_ID=$(curl -s -X POST http://localhost:8000/v2/quizzes \
  -H "Content-Type: application/json" \
  -d '{"title":"Math Test","shuffle_questions":true}' | jq '.id')

# 2. Add question
curl -X POST http://localhost:8000/v2/quizzes/$QUIZ_ID/questions \
  -H "Content-Type: application/json" \
  -d '{
    "text":"2+2=?",
    "points":1,
    "order_number":1,
    "answers":[
      {"text":"4","is_correct":true},
      {"text":"3","is_correct":false}
    ]
  }'

# 3. Publish
curl -X PATCH http://localhost:8000/v2/quizzes/$QUIZ_ID/publish
```

### Test in Telegram Bot

1. Start conversation: `/start`
2. Enter: `TestUser test@example.com`
3. Select category
4. Select quiz
5. Answer questions
6. View results

## 🧪 Testing

### Run Sample Data

```bash
python create_sample_data.py
```

Creates:

- 2 categories (Matematika, English)
- 2 published quizzes with sample questions
- 2 test students (ali@test.com, vali@test.com)

### Test API Endpoints

See **[DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)** for testing commands and examples.

## 🔐 Security Features

- ✅ Question shuffling (prevents memorization)
- ✅ Answer shuffling (anti-cheating)
- ✅ Answer history audit trail
- ✅ Timestamp validation
- ✅ CORS enabled
- ⏳ Time limit enforcement (Phase 2)

## 📊 Database Schema

**Core Tables:**

- `quizzes` - Quiz metadata with shuffle options
- `questions` - Individual questions (multiple per quiz)
- `answers` - Answer options (2+ per question)
- `quiz_attempts` - Student quiz sessions with stats
- `attempt_answers` - Individual submitted answers
- `students` - Student profiles with performance data
- `categories` - Quiz categories

**Key Stats Tracked:**

- Total attempts per student
- Average score percentage
- Last attempt timestamp
- Question-by-question answer history
- Time spent on each quiz

## 🎓 Educational Features

1. **Anti-Cheating:** Questions and answers shuffle each attempt
2. **Performance Tracking:** Student sees progress and scores
3. **Detailed Feedback:** Instant result after each quiz
4. **Category-Based Learning:** Organize quizzes by subject
5. **Progress Analytics:** Track improvement over time (Phase 2)

## 📱 Telegram Bot Commands

```
/start       - Start quiz session
/profile     - View your profile (coming Phase 2)
/leaderboard - View rankings (coming Phase 2)
/help        - Show help
```

## 🛠️ Development

### Backend Development

```bash
cd backend
python -m uvicorn app.main:app --reload
# API docs: http://localhost:8000/docs
```

### Bot Development

```bash
cd bot
python main_v2.py
```

### Frontend Development

```bash
cd webapp
npm run dev
```

## 📋 Checklist for Production

- [ ] Database migration run (`python migration_v1_to_v2.py`)
- [ ] Environment variables configured
- [ ] Bot token valid and active
- [ ] Sample quizzes created
- [ ] API endpoints tested
- [ ] Telegram bot tested end-to-end
- [ ] Shuffle features verified
- [ ] Admin panel accessible
- [ ] Docker services running

## 🐛 Troubleshooting

**Bot not responding?**

- Check BOT_TOKEN in config.py
- Verify API_BASE URL is correct
- Check backend is running: `curl http://127.0.0.1:8000/`

**Database errors?**

- Run migration: `python migration_v1_to_v2.py`
- Check Docker volume permissions

**API returns 404?**

- Ensure quiz is PUBLISHED (not DRAFT)
- Check quiz has at least one question
- Verify student email exists

See **[DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)** for more troubleshooting.

## 📞 Support

- 📖 **Documentation:** See PHASE1_GUIDE.md and DEVELOPER_GUIDE.md
- 🤖 **Bot Issues:** Check bot logs with `docker logs registon-bot`
- 🔧 **Backend Issues:** Check API docs at `http://localhost:8000/docs`
- 📧 **Questions:** Refer to implementation guides

## 📈 Roadmap

### Phase 1 ✅ (Complete)

- Professional quiz structure with questions/answers
- Quiz attempt tracking system
- Complete Telegram bot integration
- Question and answer shuffling

### Phase 2 📊 (Next)

- Analytics dashboard
- Student profiles
- Leaderboards
- Excel import/export

### Phase 3 👥 (Future)

- Role-based access control
- Advanced analytics
- Achievements system
- Mobile app

## 📄 License

REGISTON Platform © 2025

## 🤝 Contributing

This is a production platform. For improvements or bug reports, contact the development team.

---

**Status:** Phase 1 ✅ Complete & Production Ready  
**Last Updated:** June 1, 2025  
**Version:** 1.0

🚀 **Ready to use!** Start with `docker-compose up --build`
