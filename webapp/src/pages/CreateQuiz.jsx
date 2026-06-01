import { useState, useCallback } from 'react'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

const EMPTY_FORM = {
  question: '',
  option1: '',
  option2: '',
  option3: '',
  option4: '',
  correct: '1',
  category_id: '',
}

export default function CreateQuiz() {
  const [form, setForm] = useState(EMPTY_FORM)
  const [loading, setLoading] = useState(false)
  const [toast, setToast] = useState(null)

  const notify = useCallback((msg, type = 'info') => {
    setToast({ msg, type, key: Date.now() })
  }, [])

  const setField = (name) => (e) => {
    const value = e.target.value
    setForm((p) => ({ ...p, [name]: value }))
  }

  const onSubmit = async (e) => {
    e.preventDefault()

    const payload = {
      question: form.question.trim(),
      option1: form.option1.trim(),
      option2: form.option2.trim(),
      option3: form.option3.trim(),
      option4: form.option4.trim(),
      correct: Number(form.correct),
      category_id: form.category_id ? Number(form.category_id) : null,
    }

    if (!payload.question) return notify('Savol matnini kiriting.', 'error')
    const opts = [payload.option1, payload.option2, payload.option3, payload.option4]
    if (opts.some((o) => !o)) return notify('Barcha variantlarni to\'ldiring.', 'error')
    if (!(payload.correct >= 1 && payload.correct <= 4)) return notify('To\'g\'ri javob 1..4 orasida bo\'lsin.', 'error')

    setLoading(true)
    try {
      const res = await fetch(`${API_BASE}/quizzes`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })

      if (!res.ok) {
        const d = await res.json().catch(() => null)
        notify(d?.detail || 'Quiz saqlanmadi.', 'error')
        return
      }

      notify('Quiz muvaffaqiyatli saqlandi!', 'success')
      setForm(EMPTY_FORM)
    } catch {
      notify('Quiz saqlanmadi.', 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <div className="p-6 text-white bg-black min-h-screen">
        <h1 className="text-3xl mb-5 font-bold">➕ Create Quiz</h1>

        <form onSubmit={onSubmit} className="max-w-xl flex flex-col gap-3">
          <input
            value={form.question}
            onChange={setField('question')}
            placeholder="Question"
            className="w-full p-4 rounded-xl bg-zinc-900 border border-zinc-800"
          />

          <input
            value={form.option1}
            onChange={setField('option1')}
            placeholder="Option 1"
            className="w-full p-4 rounded-xl bg-zinc-900 border border-zinc-800"
          />
          <input
            value={form.option2}
            onChange={setField('option2')}
            placeholder="Option 2"
            className="w-full p-4 rounded-xl bg-zinc-900 border border-zinc-800"
          />
          <input
            value={form.option3}
            onChange={setField('option3')}
            placeholder="Option 3"
            className="w-full p-4 rounded-xl bg-zinc-900 border border-zinc-800"
          />
          <input
            value={form.option4}
            onChange={setField('option4')}
            placeholder="Option 4"
            className="w-full p-4 rounded-xl bg-zinc-900 border border-zinc-800"
          />

          <select
            value={form.correct}
            onChange={setField('correct')}
            className="w-full p-4 rounded-xl bg-zinc-900 border border-zinc-800"
          >
            <option value="1">Correct option: 1</option>
            <option value="2">Correct option: 2</option>
            <option value="3">Correct option: 3</option>
            <option value="4">Correct option: 4</option>
          </select>

          <input
            value={form.category_id}
            onChange={setField('category_id')}
            placeholder="Category ID (optional)"
            className="w-full p-4 rounded-xl bg-zinc-900 border border-zinc-800"
          />

          <button
            type="submit"
            className="bg-blue-600 px-6 py-3 rounded-xl mt-2 disabled:opacity-60"
            disabled={loading}
          >
            {loading ? 'Saving...' : 'Save Quiz'}
          </button>
        </form>

        {toast && (
          <div style={{
            marginTop: 16,
            padding: '12px 16px',
            borderRadius: 12,
            background: toast.type === 'success' ? '#15803d' : toast.type === 'error' ? '#b91c1c' : '#1e40af',
          }}>
            {toast.msg}
          </div>
        )}
      </div>
    </>
  )
}
