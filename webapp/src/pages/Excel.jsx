import { useState } from 'react'
import { api } from '../services/api'
import Spinner from '../components/Spinner'
import Toast from '../components/Toast'

export default function Excel() {
  const [file, setFile] = useState(null)
  const [importing, setImporting] = useState(false)
  const [toast, setToast] = useState(null)

  const [exporting, setExporting] = useState(false)
  const [filters, setFilters] = useState({
    start_date: '',
    end_date: '',
    quiz_id: '',
    category_id: '',
    student_id: '',
  })

  const notify = (message, type = 'info') => setToast({ type, message, duration: 4500 })

  const downloadTemplate = async () => {
    try {
      const res = await api.get('/v2/admin/export/template', { responseType: 'blob' })
      const url = URL.createObjectURL(res.data)
      const a = document.createElement('a')
      a.href = url
      a.download = 'question_template.xlsx'
      document.body.appendChild(a)
      a.click()
      a.remove()
      URL.revokeObjectURL(url)
      notify('Template downloaded', 'success')
    } catch (e) {
      notify(e?.normalizedMessage || 'Failed to download template', 'error')
    }
  }

  const exportAttempts = async () => {
    setExporting(true)
    try {
      const params = new URLSearchParams()
      ;['start_date', 'end_date', 'quiz_id', 'category_id', 'student_id'].forEach((k) => {
        if (filters[k]) params.set(k, filters[k])
      })
      const res = await api.get(`/v2/admin/export/attempts?${params.toString()}`, {
        responseType: 'blob',
      })

      const url = URL.createObjectURL(res.data)
      const a = document.createElement('a')
      a.href = url
      a.download = 'quiz_attempts_export.xlsx'
      document.body.appendChild(a)
      a.click()
      a.remove()
      URL.revokeObjectURL(url)
      notify('Export generated', 'success')
    } catch (e) {
      notify(e?.normalizedMessage || 'Failed to export attempts', 'error')
    } finally {
      setExporting(false)
    }
  }

  const importExcel = async (e) => {
    e.preventDefault()
    if (!file) {
      notify('Please select an Excel file', 'error')
      return
    }

    // Backend requires quiz_name; use a simple input-less approach by reading form fields from filters
    // But requirement says focus on functionality, so keep minimal: quiz_name=from filters.quiz_id not right.
    // We'll add basic quiz_name prompt via filters.quiz_name.
    // To avoid rewriting state schema too much, we request a quiz_name field inline here.
    const quizName = window.prompt('Quiz name for imported questions? (required)')
    if (!quizName) return
    const quizDescription = window.prompt('Quiz description (optional)') || ''

    const formData = new FormData()
    formData.append('file', file)
    formData.append('quiz_name', quizName)
    formData.append('quiz_description', quizDescription)
    if (filters.category_id) formData.append('category_id', filters.category_id)

    setImporting(true)
    try {
      await api.post('/v2/admin/import/excel', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      notify('Excel imported successfully', 'success')
      setFile(null)
    } catch (e2) {
      notify(e2?.normalizedMessage || 'Import failed', 'error')
    } finally {
      setImporting(false)
    }
  }

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-bold">Excel</h1>
        <div className="text-sm text-slate-400 mt-1">Upload, download template, export attempts</div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <section className="rounded-2xl border border-slate-800 bg-slate-900/30 p-4">
          <div className="text-sm font-semibold">Upload Excel</div>
          <form onSubmit={importExcel} className="mt-4 space-y-3">
            <input
              type="file"
              accept=".xlsx"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              className="block w-full text-sm text-slate-200 file:mr-3 file:py-2 file:px-3 file:rounded-xl file:border-0 file:bg-blue-600/20 file:text-blue-200"
            />

            <div className="flex flex-col gap-1">
              <label className="text-xs text-slate-400">Category ID (optional for import)</label>
              <input
                className="rounded-xl border border-slate-800 bg-slate-950 px-3 py-2 text-slate-100"
                value={filters.category_id}
                onChange={(e) => setFilters((p) => ({ ...p, category_id: e.target.value }))}
                placeholder="e.g. 1"
              />
            </div>

            <div className="flex items-center gap-3">
              <button
                type="submit"
                disabled={importing}
                className="px-4 py-2 rounded-xl bg-blue-600 text-white font-semibold disabled:opacity-60 flex items-center gap-2"
              >
                {importing ? <Spinner className="w-4 h-4" /> : null}
                {importing ? 'Importing...' : 'Import'}
              </button>

              <button
                type="button"
                onClick={downloadTemplate}
                disabled={importing}
                className="px-4 py-2 rounded-xl border border-slate-800 text-slate-200 hover:bg-slate-900"
              >
                Download template
              </button>
            </div>

            <div className="text-xs text-slate-400">
              After selecting a file, you will be asked for <span className="text-slate-200 font-medium">quiz name</span>.
            </div>
          </form>
        </section>

        <section className="rounded-2xl border border-slate-800 bg-slate-900/30 p-4">
          <div className="text-sm font-semibold">Export attempts</div>

          <div className="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-3">
            {[
              { key: 'start_date', label: 'Start date (YYYY-MM-DD)' },
              { key: 'end_date', label: 'End date (YYYY-MM-DD)' },
              { key: 'quiz_id', label: 'Quiz ID' },
              { key: 'category_id', label: 'Category ID' },
              { key: 'student_id', label: 'Student ID' },
            ].map(({ key, label }) => (
              <div key={key} className="flex flex-col gap-1">
                <label className="text-xs text-slate-400">{label}</label>
                <input
                  value={filters[key]}
                  onChange={(e) => setFilters((p) => ({ ...p, [key]: e.target.value }))}
                  className="rounded-xl border border-slate-800 bg-slate-950 px-3 py-2 text-slate-100"
                />
              </div>
            ))}
          </div>

          <div className="mt-4 flex items-center gap-3">
            <button
              type="button"
              disabled={exporting}
              onClick={exportAttempts}
              className="px-4 py-2 rounded-xl bg-emerald-600/20 border border-emerald-500/30 text-emerald-200 font-semibold disabled:opacity-60 flex items-center gap-2"
            >
              {exporting ? <Spinner className="w-4 h-4" /> : null}
              {exporting ? 'Exporting...' : 'Export to Excel'}
            </button>
          </div>
        </section>
      </div>

      <Toast toast={toast} onClose={() => setToast(null)} />
    </div>
  )
}

