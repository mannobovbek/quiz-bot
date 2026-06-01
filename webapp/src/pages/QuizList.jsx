import { useCallback, useEffect, useState } from 'react'
import { api } from '../services/api'
import Spinner from '../components/Spinner'
import Toast from '../components/Toast'
import ConfirmDialog from '../components/ui/ConfirmDialog'

const EMPTY = {
  title: '',
  description: '',
  category_id: '',
  time_limit: 0,
  shuffle_questions: true,
  shuffle_answers: true,
  show_result: true,
}

export default function QuizList() {
  const [quizzes, setQuizzes] = useState([])
  const [loading, setLoading] = useState(false)
  const [toast, setToast] = useState(null)

  const [form, setForm] = useState(EMPTY)
  const [editingId, setEditingId] = useState(null)
  const [submitting, setSubmitting] = useState(false)

  const [confirm, setConfirm] = useState({ open: false, quizId: null })

  const [error, setError] = useState(null)

  const notify = (message, type = 'info') => {
    setToast({ type, message, duration: 4500 })
  }

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await api.get('/v2/quizzes')
      setQuizzes(res.data || [])
    } catch (e) {
      setError(e?.normalizedMessage || 'Failed to load quizzes')
      notify(e?.normalizedMessage || 'Failed to load quizzes', 'error')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    load()
  }, [load])

  const reset = () => {
    setForm(EMPTY)
    setEditingId(null)
  }

  const startEdit = (q) => {
    setEditingId(q.id)
    setForm({
      title: q.title ?? '',
      description: q.description ?? '',
      category_id: q.category_id ?? '',
      time_limit: q.time_limit ?? 0,
      shuffle_questions: q.shuffle_questions ?? true,
      shuffle_answers: q.shuffle_answers ?? true,
      show_result: q.show_result ?? true,
    })
  }

  const onSubmit = async (e) => {
    e.preventDefault()
    if (!form.title.trim()) {
      notify('Quiz title is required', 'error')
      return
    }

    setSubmitting(true)
    try {
      const payload = {
        title: form.title.trim(),
        description: form.description.trim(),
        category_id: form.category_id ? Number(form.category_id) : null,
        time_limit: Number(form.time_limit) || 0,
        shuffle_questions: !!form.shuffle_questions,
        shuffle_answers: !!form.shuffle_answers,
        show_result: !!form.show_result,
      }

      if (editingId) {
        await api.put(`/v2/quizzes/${editingId}`, payload)
        notify('Quiz updated successfully', 'success')
      } else {
        await api.post('/v2/quizzes', payload)
        notify('Quiz created successfully', 'success')
      }
      reset()
      await load()
    } catch (e2) {
      notify(e2?.normalizedMessage || 'Failed to save quiz', 'error')
    } finally {
      setSubmitting(false)
    }
  }

  const askDelete = (id) => setConfirm({ open: true, quizId: id })

  const doDelete = async () => {
    const id = confirm.quizId
    setConfirm({ open: false, quizId: null })
    if (!id) return
    try {
      await api.delete(`/v2/quizzes/${id}`)
      notify('Quiz deleted', 'success')
      if (editingId === id) reset()
      await load()
    } catch (e) {
      notify(e?.normalizedMessage || 'Failed to delete quiz', 'error')
    }
  }

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-bold">Quiz List</h1>
        <div className="text-sm text-slate-400 mt-1">Create, edit, delete quizzes</div>
      </div>

      <div className="rounded-2xl border border-slate-800 bg-slate-900/30 p-4">
        <div className="text-sm font-semibold">{editingId ? 'Edit quiz' : 'Create quiz'}</div>
        <form onSubmit={onSubmit} className="mt-4 grid grid-cols-1 lg:grid-cols-2 gap-3">
          <div className="flex flex-col gap-1">
            <label className="text-xs text-slate-400">Title</label>
            <input
              className="rounded-xl border border-slate-800 bg-slate-950 px-3 py-2 text-slate-100"
              value={form.title}
              onChange={(e) => setForm((p) => ({ ...p, title: e.target.value }))}
            />
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-xs text-slate-400">Category ID (optional)</label>
            <input
              className="rounded-xl border border-slate-800 bg-slate-950 px-3 py-2 text-slate-100"
              value={form.category_id}
              onChange={(e) => setForm((p) => ({ ...p, category_id: e.target.value }))}
            />
          </div>

          <div className="flex flex-col gap-1 lg:col-span-2">
            <label className="text-xs text-slate-400">Description</label>
            <input
              className="rounded-xl border border-slate-800 bg-slate-950 px-3 py-2 text-slate-100"
              value={form.description}
              onChange={(e) => setForm((p) => ({ ...p, description: e.target.value }))}
            />
          </div>

          <div className="flex flex-col gap-1">
            <label className="text-xs text-slate-400">Time limit (seconds)</label>
            <input
              type="number"
              className="rounded-xl border border-slate-800 bg-slate-950 px-3 py-2 text-slate-100"
              value={form.time_limit}
              onChange={(e) => setForm((p) => ({ ...p, time_limit: e.target.value }))}
            />
          </div>

          <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between sm:gap-4">
            <label className="flex items-center gap-2 text-xs text-slate-300">
              <input
                type="checkbox"
                checked={!!form.shuffle_questions}
                onChange={(e) => setForm((p) => ({ ...p, shuffle_questions: e.target.checked }))}
              />
              Shuffle questions
            </label>
            <label className="flex items-center gap-2 text-xs text-slate-300">
              <input
                type="checkbox"
                checked={!!form.shuffle_answers}
                onChange={(e) => setForm((p) => ({ ...p, shuffle_answers: e.target.checked }))}
              />
              Shuffle answers
            </label>
            <label className="flex items-center gap-2 text-xs text-slate-300">
              <input
                type="checkbox"
                checked={!!form.show_result}
                onChange={(e) => setForm((p) => ({ ...p, show_result: e.target.checked }))}
              />
              Show result
            </label>
          </div>

          <div className="lg:col-span-2 flex items-center gap-3">
            <button
              type="submit"
              className="px-4 py-2 rounded-xl bg-blue-600 text-white font-semibold disabled:opacity-60 flex items-center gap-2"
              disabled={submitting}
            >
              {submitting ? <Spinner className="w-4 h-4" /> : null}
              {editingId ? 'Update' : 'Create'}
            </button>
            {editingId && (
              <button
                type="button"
                className="px-4 py-2 rounded-xl border border-slate-800 text-slate-200 hover:bg-slate-900"
                onClick={reset}
                disabled={submitting}
              >
                Cancel
              </button>
            )}
          </div>
        </form>
      </div>

      <div className="rounded-2xl border border-slate-800 bg-slate-900/30 p-4">
        <div className="flex items-center justify-between">
          <div className="text-sm font-semibold">All Quizzes</div>
          <div className="text-xs text-slate-400">{quizzes.length} total</div>
        </div>

        {loading ? (
          <div className="mt-4 flex items-center gap-3 text-slate-300">
            <Spinner className="w-6 h-6" />
            Loading...
          </div>
        ) : error ? (
          <div className="mt-4 rounded-xl border border-rose-500/30 bg-rose-500/10 text-rose-200 p-4">{error}</div>
        ) : (
          <div className="mt-4 overflow-x-auto">
            <table className="min-w-[900px] w-full text-sm">
              <thead className="text-slate-400">
                <tr className="text-left border-b border-slate-800">
                  <th className="py-2 px-2">ID</th>
                  <th className="py-2 px-2">Title</th>
                  <th className="py-2 px-2">Description</th>
                  <th className="py-2 px-2">Category</th>
                  <th className="py-2 px-2">Status</th>
                  <th className="py-2 px-2">Actions</th>
                </tr>
              </thead>
              <tbody>
                {quizzes.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="py-10 text-center text-slate-500">
                      No quizzes.
                    </td>
                  </tr>
                ) : (
                  quizzes.map((q) => (
                    <tr key={q.id} className="border-b border-slate-800/60">
                      <td className="py-2 px-2 text-slate-300">{q.id}</td>
                      <td className="py-2 px-2 text-slate-200 font-medium">{q.title}</td>
                      <td className="py-2 px-2 text-slate-400 max-w-[320px]">{q.description || '-'}</td>
                      <td className="py-2 px-2 text-slate-200">{q.category_id ?? '-'}</td>
                      <td className="py-2 px-2 text-slate-200">{q.status ?? '-'}</td>
                      <td className="py-2 px-2">
                        <div className="flex gap-2 flex-wrap">
                          <button
                            className="px-3 py-1.5 rounded-xl border border-slate-800 text-slate-100 hover:bg-slate-900"
                            onClick={() => startEdit(q)}
                          >
                            Edit
                          </button>
                          <button
                            className="px-3 py-1.5 rounded-xl bg-rose-600/15 border border-rose-500/30 text-rose-200 hover:bg-rose-600/25"
                            onClick={() => askDelete(q.id)}
                          >
                            Delete
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <ConfirmDialog
        open={confirm.open}
        title="Delete quiz?"
        message="This will delete the quiz. This action cannot be undone."
        confirmText="Delete"
        cancelText="Cancel"
        danger
        onCancel={() => setConfirm({ open: false, quizId: null })}
        onConfirm={doDelete}
      />

      <Toast toast={toast} onClose={() => setToast(null)} />
    </div>
  )
}

