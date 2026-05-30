import { useEffect, useState } from 'react'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

export default function Dashboard() {
  const [analytics, setAnalytics] = useState({ students: 0, quizzes: 0, avg_score: 0 })
  const [quizzes, setQuizzes] = useState([])
  const [form, setForm] = useState({ question: '', option1: '', option2: '', option3: '', option4: '', correct: '1' })
  const [message, setMessage] = useState('')

  useEffect(() => {
    fetch(`${API_BASE}/analytics`)
      .then((res) => res.json())
      .then(setAnalytics)
      .catch(() => setMessage('Unable to load analytics.'))

    loadQuizzes()
  }, [])

  const loadQuizzes = () => {
    fetch(`${API_BASE}/quizzes`)
      .then((res) => res.json())
      .then(setQuizzes)
      .catch(() => setMessage('Unable to load quizzes.'))
  }

  const handleChange = (event) => {
    const { name, value } = event.target
    setForm((prev) => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setMessage('Saving quiz...')

    const payload = {
      question: form.question,
      option1: form.option1,
      option2: form.option2,
      option3: form.option3,
      option4: form.option4,
      correct: Number(form.correct),
    }

    const response = await fetch(`${API_BASE}/quizzes`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })

    if (!response.ok) {
      setMessage('Could not save quiz. Check your values.')
      return
    }

    setForm({ question: '', option1: '', option2: '', option3: '', option4: '', correct: '1' })
    setMessage('Quiz saved successfully.')
    loadQuizzes()
  }

  const handleDelete = async (id) => {
    await fetch(`${API_BASE}/quizzes/${id}`, { method: 'DELETE' })
    loadQuizzes()
  }

  return (
    <div className="dashboard-root">
      <div className="dashboard-container">
        <h1 className="admin-title">🏛 REGISTON ADMIN PANEL</h1>

        <div className="stats-grid">
          <div className="card">
            <p className="label">Students</p>
            <p className="text-3xl font-semibold">{analytics.students}</p>
          </div>
          <div className="card">
            <p className="label">Quizzes</p>
            <p className="text-3xl font-semibold">{analytics.quizzes}</p>
          </div>
          <div className="card">
            <p className="label">Avg score</p>
            <p className="text-3xl font-semibold">{analytics.avg_score}%</p>
          </div>
        </div>

        <div className="main-grid">
          <section className="card">
            <h2 className="card-title">➕ Create new quiz</h2>
            <form onSubmit={handleSubmit} className="form-grid">
              <label>
                <span className="label">Question</span>
                <textarea
                  name="question"
                  value={form.question}
                  onChange={handleChange}
                  className="textarea"
                />
              </label>
              <input
                name="option1"
                value={form.option1}
                onChange={handleChange}
                className="input"
                placeholder="Option 1"
              />
              <input
                name="option2"
                value={form.option2}
                onChange={handleChange}
                className="input"
                placeholder="Option 2"
              />
              <input
                name="option3"
                value={form.option3}
                onChange={handleChange}
                className="input"
                placeholder="Option 3"
              />
              <input
                name="option4"
                value={form.option4}
                onChange={handleChange}
                className="input"
                placeholder="Option 4"
              />
              <div className="input-row">
                <label>
                  <span className="label">Correct option</span>
                  <select
                    name="correct"
                    value={form.correct}
                    onChange={handleChange}
                    className="select"
                  >
                    <option value="1">Option 1</option>
                    <option value="2">Option 2</option>
                    <option value="3">Option 3</option>
                    <option value="4">Option 4</option>
                  </select>
                </label>
                <button type="submit" className="button">
                  Save Quiz
                </button>
              </div>
            </form>
            {message && <p className="message">{message}</p>}
          </section>

          <section className="card">
            <h2 className="card-title">📚 Quiz list</h2>
            {quizzes.length === 0 ? (
              <p className="label">No quizzes yet.</p>
            ) : (
              <div className="quiz-list">
                {quizzes.map((quiz) => (
                  <div key={quiz.id} className="quiz-item">
                    <p className="font-semibold">{quiz.question}</p>
                    <ul>
                      <li>1. {quiz.option1}</li>
                      <li>2. {quiz.option2}</li>
                      <li>3. {quiz.option3}</li>
                      <li>4. {quiz.option4}</li>
                    </ul>
                    <p className="label">Correct option: {quiz.correct}</p>
                    <button onClick={() => handleDelete(quiz.id)} className="delete-button">
                      Delete
                    </button>
                  </div>
                ))}
              </div>
            )}
          </section>
        </div>
      </div>
    </div>
  )
}
