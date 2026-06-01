# PHASE 2: Analytics & Dashboard - Implementation Guide

## 📋 Overview

Phase 2 adds professional analytics, dashboards, student profiles, and leaderboards. This makes REGISTON a complete LMS with insights and gamification.

### Phase 2 Goals

- 📊 Admin dashboard with analytics
- 👤 Student profiles with history
- 🏆 Leaderboards (global & category)
- 📤 Excel import/export
- 📈 Performance tracking

### Success Criteria

- ✅ Dashboard shows real-time metrics
- ✅ Students can see their profiles and history
- ✅ Leaderboards display top performers
- ✅ Bulk upload works with Excel files
- ✅ Results can be exported to Excel

---

## 🏗️ Architecture

### Backend Layer

```
services/
  ├── analytics.py      # Calculate dashboard metrics
  ├── leaderboard.py    # Generate leaderboard rankings
  └── excel_handler.py  # Import/export Excel files

main.py (new endpoints)
  ├── /v2/admin/analytics
  ├── /v2/admin/top-quizzes
  ├── /v2/admin/difficult-questions
  ├── /v2/admin/recent-attempts
  ├── /v2/students/{id}/profile
  ├── /v2/leaderboard
  ├── /v2/leaderboard/category/{id}
  ├── /v2/admin/import/excel
  └── /v2/admin/export/attempts
```

### Frontend Layer

```
webapp/src/pages/
  ├── AdminDashboard.jsx      # Analytics dashboard
  ├── StudentProfile.jsx      # Student history
  └── Leaderboard.jsx         # Rankings display

webapp/src/components/
  ├── AnalyticsCard.jsx       # Stats card component
  ├── ExcelUpload.jsx         # File upload form
  ├── LeaderboardTable.jsx    # Rankings table
  └── AttemptsList.jsx        # History list
```

---

## 📊 Analytics Service

### What Gets Tracked

#### Dashboard Metrics

- **Total Students** - Count of all registered students
- **Total Quizzes** - Count of published quizzes
- **Today's Submissions** - Count of attempts started today
- **Average Score** - Mean percentage across all attempts
- **Quiz Performance** - Most completed, highest-scoring quizzes
- **Question Difficulty** - Lowest pass rates, most missed

#### Leaderboard Data

- **Global Top 10** - Highest average score overall
- **Category Top 10** - Highest average in specific category
- **Student Rank** - Position in global/category rankings
- **Study Streak** - Days in a row with quiz attempts

### Calculation Examples

```python
# Average score across all attempts
avg_score = sum(attempt.percentage for all attempts) / count

# Pass rate for a question
pass_rate = (correct_answers / total_answers) * 100

# Student rank
rank = count of students with higher avg_score + 1

# Top quiz
sorted by (attempt_count DESC, avg_score DESC)
```

---

## 📤 Excel Features

### Excel Import Format

**File Format: .xlsx with sheet named "Questions"**

| Savol (Question)   | A (Option 1) | B (Option 2) | C (Option 3) | D (Option 4) | To'g'ri (Correct) |
| ------------------ | ------------ | ------------ | ------------ | ------------ | ----------------- |
| Capital of France? | London       | Paris        | Berlin       | Madrid       | B                 |
| 2 + 2 = ?          | 3            | 4            | 5            | 6            | B                 |

**Processing Steps:**

1. Validate file format and sheet name
2. Extract rows
3. Validate all 6 columns present
4. Validate correct answer is A/B/C/D
5. Create quiz with questions
6. Create 4 answers per question
7. Mark correct answer
8. Return created quiz ID

---

## 🔌 API Endpoints (Phase 2)

### 1. Analytics Dashboard

**GET /v2/admin/analytics**

Returns dashboard metrics with real-time stats.

### 2. Top Quizzes

**GET /v2/admin/top-quizzes?limit=10**

Most completed and highest-scoring quizzes.

### 3. Difficult Questions

**GET /v2/admin/difficult-questions?limit=10**

Questions with lowest pass rates.

### 4. Recent Attempts

**GET /v2/admin/recent-attempts?limit=20**

Latest quiz submissions.

### 5. Student Profile

**GET /v2/students/{id}/profile**

Detailed student info with attempt history.

### 6. Global Leaderboard

**GET /v2/leaderboard?limit=10&period=all**

Top students globally. Period: "all", "week", "month"

### 7. Category Leaderboard

**GET /v2/leaderboard/category/{id}?limit=10&period=all**

Top students in specific category.

### 8. Excel Import

**POST /v2/admin/import/excel**

Bulk upload questions from .xlsx file.

### 9. Excel Export

**GET /v2/admin/export/attempts**

Download attempt results as .xlsx

---

## 🚀 Implementation Steps

### Step 1: Add Dependencies

```bash
pip install openpyxl python-multipart
```

### Step 2: Create Backend Services

1. `backend/app/services/analytics.py` - Analytics calculations
2. `backend/app/services/leaderboard.py` - Leaderboard queries
3. `backend/app/services/excel_handler.py` - Excel import/export

### Step 3: Add API Endpoints

Add 9 endpoints to `backend/app/main.py`

### Step 4: Create Frontend Pages

1. AdminDashboard.jsx
2. StudentProfile.jsx
3. Leaderboard.jsx
4. Supporting components

### Step 5: Update Routing

Add new routes to App.jsx

### Step 6: Test & Document

Verify all endpoints and create examples.

---

## 📦 Files to Create

**Backend:**

- `backend/app/services/analytics.py`
- `backend/app/services/leaderboard.py`
- `backend/app/services/excel_handler.py`

**Frontend:**

- `webapp/src/pages/AdminDashboard.jsx`
- `webapp/src/pages/StudentProfile.jsx`
- `webapp/src/pages/Leaderboard.jsx`
- `webapp/src/components/AnalyticsCard.jsx`
- `webapp/src/components/ExcelUpload.jsx`
- `webapp/src/components/LeaderboardTable.jsx`
- `webapp/src/components/AttemptsList.jsx`

---

## ✅ Testing Checklist

- [ ] Admin dashboard loads with metrics
- [ ] Top quizzes ranking is accurate
- [ ] Difficult questions sorted by pass rate
- [ ] Excel import creates quiz correctly
- [ ] Excel export downloads file
- [ ] Leaderboard shows top students
- [ ] Student profile shows history
- [ ] Category filter works
- [ ] All endpoints return 200 on success
- [ ] Error cases handled properly

---

## 🎯 Phase 2 Complete When:

1. ✅ All 9 endpoints working
2. ✅ Dashboard shows analytics
3. ✅ Excel import/export functional
4. ✅ Leaderboards displaying
5. ✅ Student profiles working
6. ✅ Frontend pages created
7. ✅ All tested and documented
