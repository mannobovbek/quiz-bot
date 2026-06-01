# 🚀 REGISTON Phase 1 - Deployment Checklist

## Pre-Deployment

- [ ] **Database Backup** - Backup existing data before migration

  ```bash
  sqlite3 test.db ".dump" > backup.sql
  ```

- [ ] **Python Version** - Python 3.9+

  ```bash
  python --version
  ```

- [ ] **Dependencies** - All packages installed

  ```bash
  pip install fastapi sqlalchemy aiogram pydantic python-multipart
  ```

- [ ] **Config Files** - Check `.env` or config.py
  ```
  BOT_TOKEN=your_token
  API_BASE=http://127.0.0.1:8000
  CHANNEL_ID=@yourchannel
  ```

---

## Migration

- [ ] **Run Migration Script**

  ```bash
  python migration_v1_to_v2.py
  ```

  Expected output:

  ```
  ✅ Tables created successfully!
  ✅ Columns added!
  ✅ Legacy quizzes migrated!
  ```

- [ ] **Verify Database**

  ```bash
  sqlite3 test.db ".tables"
  # Should show: answers attempts attempt_answers categories
  #             questions quiz_attempts quizzes students
  ```

- [ ] **Create Sample Data** (optional but recommended)
  ```bash
  python create_sample_data.py
  ```
  Creates test quizzes and students for immediate testing

---

## Backend Setup

- [ ] **Start Backend**

  ```bash
  cd backend
  python -m uvicorn app.main:app --reload
  ```

  Expected: `Uvicorn running on http://127.0.0.1:8000`

- [ ] **Test API**

  ```bash
  curl http://127.0.0.1:8000/
  # Response: {"status":"ok","project":"REGISTON"}
  ```

- [ ] **Check API Docs**
      Open: `http://127.0.0.1:8000/docs`
      Should show Swagger UI with all v2 endpoints

- [ ] **Test Endpoints**

  ```bash
  # List quizzes
  curl http://127.0.0.1:8000/v2/quizzes

  # List categories
  curl http://127.0.0.1:8000/categories
  ```

---

## Bot Setup

- [ ] **Verify Bot Token**

  ```bash
  curl https://api.telegram.org/botYOUR_TOKEN/getMe
  ```

  Should return bot info (no errors)

- [ ] **Update Bot File** - Use new version

  ```bash
  # Backup old
  cp bot/main.py bot/main_legacy.py

  # Use new professional bot
  # Option A: Copy file
  cp bot/main_v2.py bot/main.py

  # Option B: Update docker-compose.yml to use main_v2.py
  ```

- [ ] **Test Bot Start**

  ```bash
  python bot/main_v2.py
  ```

  Expected: `🤖 Bot ishga tushdi!`

- [ ] **Telegram Test**
  - Message your bot: `/start`
  - Enter email: `test@example.com`
  - Verify you can navigate menus

---

## Docker Deployment

- [ ] **Build Images**

  ```bash
  docker-compose build
  ```

- [ ] **Start Services**

  ```bash
  docker-compose up -d
  ```

- [ ] **Verify Services Running**

  ```bash
  docker-compose ps
  # Should show: registon-backend, registon-bot, registon-db, registon-webapp
  ```

- [ ] **Check Logs**

  ```bash
  docker-compose logs -f backend
  docker-compose logs -f bot
  ```

- [ ] **Test Backend in Container**
  ```bash
  curl http://127.0.0.1:8000/docs
  ```

---

## Data Verification

- [ ] **Categories Exist**

  ```bash
  curl http://127.0.0.1:8000/categories | jq
  # Should show categories
  ```

- [ ] **Quizzes Visible**

  ```bash
  curl http://127.0.0.1:8000/v2/quizzes | jq
  # Should show published quizzes
  ```

- [ ] **Students Registered**

  ```bash
  curl http://127.0.0.1:8000/students | jq
  # Should show students
  ```

- [ ] **Test Quiz Attempt**
  ```bash
  # Start attempt
  curl -X POST http://127.0.0.1:8000/v2/attempts/start \
    -H "Content-Type: application/json" \
    -d '{
      "quiz_id": 1,
      "student_email": "test@example.com"
    }'
  # Should return attempt_id
  ```

---

## Bot Testing

- [ ] **User Registration Flow**
  - `/start`
  - Enter: `Ali ali@gmail.com`
  - ✅ Should register successfully

- [ ] **Category Selection**
  - ✅ Should see category buttons

- [ ] **Quiz Selection**
  - ✅ Should see quiz titles

- [ ] **Question Display**
  - ✅ Question should appear
  - ✅ Answers should appear as buttons
  - ✅ Progress should show (1/3, etc)

- [ ] **Answer Submission**
  - ✅ Click answer button
  - ✅ Get feedback (✅ or ❌)
  - ✅ Score updates

- [ ] **Results Display**
  - ✅ Final score shown
  - ✅ Percentage shown
  - ✅ Duration shown

- [ ] **Back Navigation**
  - ✅ Can go back to category selection
  - ✅ Can take another quiz

---

## Shuffle Feature Verification

- [ ] **Question Shuffle**

  ```bash
  # Create attempt twice and compare question order
  # Should be different if shuffle_questions=true

  curl http://127.0.0.1:8000/v2/attempts/1/questions > q1.json
  curl http://127.0.0.1:8000/v2/attempts/2/questions > q2.json
  diff q1.json q2.json
  # Should show differences if shuffle enabled
  ```

- [ ] **Answer Shuffle**
  - Take same quiz twice in Telegram
  - ✅ Answers should be in different order each time

---

## API Testing

- [ ] **Create Quiz**

  ```bash
  curl -X POST http://127.0.0.1:8000/v2/quizzes \
    -H "Content-Type: application/json" \
    -d '{"title":"Test Quiz","shuffle_questions":true}'
  ```

  ✅ Should return quiz_id

- [ ] **Add Question**

  ```bash
  curl -X POST http://127.0.0.1:8000/v2/quizzes/1/questions \
    -H "Content-Type: application/json" \
    -d '{
      "text":"Test?",
      "points":1,
      "order_number":1,
      "answers":[
        {"text":"Yes","is_correct":true},
        {"text":"No","is_correct":false}
      ]
    }'
  ```

  ✅ Should return question_id

- [ ] **Publish Quiz**

  ```bash
  curl -X PATCH http://127.0.0.1:8000/v2/quizzes/1/publish
  ```

  ✅ Should return published status

- [ ] **Start Attempt**

  ```bash
  curl -X POST http://127.0.0.1:8000/v2/attempts/start \
    -H "Content-Type: application/json" \
    -d '{"quiz_id":1,"student_email":"test@test.com"}'
  ```

  ✅ Should return attempt_id

- [ ] **Get Questions**

  ```bash
  curl http://127.0.0.1:8000/v2/attempts/1/questions
  ```

  ✅ Should return questions with shuffled answers

- [ ] **Submit Answer**

  ```bash
  curl -X POST http://127.0.0.1:8000/v2/attempts/1/answer \
    -H "Content-Type: application/json" \
    -d '{"question_id":1,"selected_answer_id":1}'
  ```

  ✅ Should return is_correct and updated score

- [ ] **Finish Attempt**

  ```bash
  curl -X POST http://127.0.0.1:8000/v2/attempts/1/finish
  ```

  ✅ Should return final score and percentage

- [ ] **View Results**
  ```bash
  curl http://127.0.0.1:8000/v2/attempts/1
  ```
  ✅ Should show full attempt details with all answers

---

## Performance Testing

- [ ] **Load API with Multiple Requests**

  ```bash
  for i in {1..100}; do
    curl -s http://127.0.0.1:8000/v2/quizzes
  done
  ```

  ✅ Should handle without errors

- [ ] **Check Database Performance**

  ```bash
  sqlite3 test.db "VACUUM;"
  ```

- [ ] **Monitor Logs for Errors**
  ```bash
  docker-compose logs | grep -i error
  ```
  ✅ Should be minimal/none

---

## Documentation Verification

- [ ] **README.md** - Updated and comprehensive

  ```bash
  cat README.md | head -50
  ```

- [ ] **PHASE1_GUIDE.md** - Complete API reference

  ```bash
  wc -l PHASE1_GUIDE.md
  # Should be 500+ lines
  ```

- [ ] **DEVELOPER_GUIDE.md** - Quick reference

  ```bash
  wc -l DEVELOPER_GUIDE.md
  # Should be 400+ lines
  ```

- [ ] **API Documentation** - Auto-generated
      Open: `http://127.0.0.1:8000/docs`
      ✅ Should show all v2 endpoints

---

## Security Checklist

- [ ] **CORS Enabled** - For web frontend

  ```bash
  curl -i -H "Origin: http://localhost:3000" \
    http://127.0.0.1:8000/
  ```

  ✅ Should see Access-Control headers

- [ ] **Input Validation** - Try invalid data

  ```bash
  curl -X POST http://127.0.0.1:8000/v2/quizzes \
    -d '{"title":""}'
  ```

  ✅ Should return 422 validation error

- [ ] **Error Handling** - Try non-existent resources
  ```bash
  curl http://127.0.0.1:8000/v2/quizzes/99999
  ```
  ✅ Should return 404 with detail message

---

## Final Checks

- [ ] **All Services Running**

  ```bash
  docker-compose ps
  ```

- [ ] **No Error Logs**

  ```bash
  docker-compose logs | grep -i "error\|fail" | wc -l
  # Should be 0 or minimal
  ```

- [ ] **Database Healthy**

  ```bash
  sqlite3 test.db "SELECT COUNT(*) FROM sqlite_master WHERE type='table';"
  # Should show 8+ tables
  ```

- [ ] **Bot Responsive**
  - Message bot: `/start`
  - Should respond within 2 seconds

- [ ] **API Fast**
  ```bash
  time curl http://127.0.0.1:8000/v2/quizzes
  # Should complete in < 500ms
  ```

---

## Deployment Confirmation

✅ **All checks passed?**

If YES, your REGISTON Phase 1 platform is:

- ✅ Properly installed
- ✅ Fully functional
- ✅ Ready for production use
- ✅ Ready for Phase 2 development

---

## Common Issues & Solutions

### Issue: `Tables already exist`

**Solution:**

```bash
# Backup data first
sqlite3 test.db ".dump" > backup.sql

# Drop old tables (careful!)
sqlite3 test.db << EOF
DROP TABLE IF EXISTS attempt_answers;
DROP TABLE IF EXISTS attempt_answer;
DROP TABLE IF EXISTS quiz_attempts;
DROP TABLE IF EXISTS questions;
DROP TABLE IF EXISTS answers;
EOF

# Re-run migration
python migration_v1_to_v2.py
```

### Issue: Bot doesn't respond

**Solution:**

```bash
# Check BOT_TOKEN
grep BOT_TOKEN bot/config.py

# Check API endpoint
curl http://127.0.0.1:8000/

# Restart bot
docker-compose restart bot
docker-compose logs bot
```

### Issue: API returns 404

**Solution:**

```bash
# Ensure quiz is PUBLISHED
curl http://127.0.0.1:8000/v2/quizzes | jq '.[] | {id, status, title}'

# Check quiz has questions
curl http://127.0.0.1:8000/v2/quizzes/1
```

---

## Need Help?

1. Check **DEVELOPER_GUIDE.md** for common tasks
2. Check **PHASE1_GUIDE.md** for detailed API docs
3. Check API docs at `http://localhost:8000/docs`
4. Check logs: `docker-compose logs -f`

---

## After Deployment

1. ✅ Celebrate Phase 1 completion! 🎉
2. ✅ Create sample quizzes for testing
3. ✅ Get admin user created
4. ✅ Start Phase 2 planning
5. ✅ Get user feedback

---

**Date:** June 1, 2025  
**Version:** 1.0  
**Status:** Production Ready ✅

🚀 **Ready to deploy!**
