import { useEffect, useMemo, useState } from 'react'
import { api } from '../services/api'
import Spinner from '../components/Spinner'
import Toast from '../components/Toast'

export default function Leaderboard() {
  const [globalLoading, setGlobalLoading] = useState(true)
  const [categoryLoading, setCategoryLoading] = useState(false)

  const [period, setPeriod] = useState('all')

  const [globalRows, setGlobalRows] = useState([])
  const [categoryRows, setCategoryRows] = useState([])

  const [categories, setCategories] = useState([])
  const [selectedCategoryId, setSelectedCategoryId] = useState('')

  const [toast, setToast] = useState(null)
  const notify = (message, type = 'info') => setToast({ type, message, duration: 4500 })

  useEffect(() => {
    let mounted = true
    ;(async () => {
      try {
        const [catRes, lbRes] = await Promise.all([
          api.get('/categories'),
          api.get(`/v2/leaderboard?limit=50&offset=0&period=${encodeURIComponent(period)}`),
        ])
        if (!mounted) return
        setCategories(catRes.data || [])
        setGlobalRows(lbRes.data?.students || lbRes.data || [])
        if (catRes.data?.length) setSelectedCategoryId(String(catRes.data[0].id))
      } catch (e) {
        notify(e?.normalizedMessage || 'Failed to load leaderboard', 'error')
      } finally {
        if (mounted) setGlobalLoading(false)
      }
    })()
    return () => {
      mounted = false
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    let mounted = true
    ;(async () => {
      setGlobalLoading(true)
      try {
        const res = await api.get(`/v2/leaderboard?limit=50&offset=0&period=${encodeURIComponent(period)}`)
        if (!mounted) return
        setGlobalRows(res.data?.students || res.data || [])
      } catch (e) {
        notify(e?.normalizedMessage || 'Failed to load global leaderboard', 'error')
      } finally {
        if (mounted) setGlobalLoading(false)
      }
    })()
    return () => {
      mounted = false
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [period])

  const loadCategory = async (catId) => {
    if (!catId) return
    setCategoryLoading(true)
    try {
      const res = await api.get(
        `/v2/leaderboard/category/${catId}?limit=50&offset=0&period=${encodeURIComponent(period)}`
      )
      setCategoryRows(res.data?.students || res.data || [])
    } catch (e) {
      notify(e?.normalizedMessage || 'Failed to load category leaderboard', 'error')
    } finally {
      setCategoryLoading(false)
    }
  }

  useEffect(() => {
    if (!selectedCategoryId) return
    loadCategory(selectedCategoryId)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedCategoryId, period])

  const rowsWithFallback = useMemo(() => globalRows || [], [globalRows])

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-bold">Leaderboard</h1>
        <div className="text-sm text-slate-400 mt-1">Global and category rankings</div>
      </div>

      <div className="rounded-2xl border border-slate-800 bg-slate-900/30 p-4">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="text-sm font-semibold">Period</div>
            <select
              className="rounded-xl border border-slate-800 bg-slate-950 px-3 py-2 text-slate-100"
              value={period}
              onChange={(e) => setPeriod(e.target.value)}
            >
              <option value="all">All time</option>
              <option value="week">This week</option>
              <option value="month">This month</option>
            </select>
          </div>

          <div className="flex items-center gap-3">
            <div className="text-sm font-semibold">Category</div>
            <select
              className="rounded-xl border border-slate-800 bg-slate-950 px-3 py-2 text-slate-100"
              value={selectedCategoryId}
              onChange={(e) => setSelectedCategoryId(e.target.value)}
            >
              <option value="">Select category</option>
              {categories.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <section className="rounded-2xl border border-slate-800 bg-slate-900/30 p-4">
          <div className="text-sm font-semibold">Global leaderboard</div>
          {globalLoading ? (
            <div className="mt-4 flex items-center gap-3 text-slate-300">
              <Spinner className="w-6 h-6" />
              Loading...
            </div>
          ) : (
            <div className="mt-4 overflow-x-auto">
              <table className="min-w-[640px] w-full text-sm">
                <thead className="text-slate-400">
                  <tr className="text-left border-b border-slate-800">
                    <th className="py-2 px-2">#</th>
                    <th className="py-2 px-2">Student</th>
                    <th className="py-2 px-2">Average</th>
                    <th className="py-2 px-2">Attempts</th>
                  </tr>
                </thead>
                <tbody>
                  {rowsWithFallback.length === 0 ? (
                    <tr>
                      <td colSpan={4} className="py-10 text-center text-slate-500">
                        No data
                      </td>
                    </tr>
                  ) : (
                    rowsWithFallback.map((r, idx) => (
                      <tr key={r.student_id || r.id || idx} className="border-b border-slate-800/60">
                        <td className="py-2 px-2 text-slate-300">{idx + 1}</td>
                        <td className="py-2 px-2 text-slate-200 font-medium">{r.name || r.student_name || r.student?.name || r.student_email || '-'}</td>
                        <td className="py-2 px-2 text-emerald-200 font-semibold">{r.average_score != null ? r.average_score : r.avg_percentage != null ? r.avg_percentage : '-'}</td>
                        <td className="py-2 px-2 text-slate-200">{r.attempts_count ?? r.attempts ?? '-'}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          )}
        </section>

        <section className="rounded-2xl border border-slate-800 bg-slate-900/30 p-4">
          <div className="text-sm font-semibold">Category leaderboard</div>
          {categoryLoading ? (
            <div className="mt-4 flex items-center gap-3 text-slate-300">
              <Spinner className="w-6 h-6" />
              Loading...
            </div>
          ) : (
            <div className="mt-4 overflow-x-auto">
              <table className="min-w-[640px] w-full text-sm">
                <thead className="text-slate-400">
                  <tr className="text-left border-b border-slate-800">
                    <th className="py-2 px-2">#</th>
                    <th className="py-2 px-2">Student</th>
                    <th className="py-2 px-2">Average</th>
                    <th className="py-2 px-2">Attempts</th>
                  </tr>
                </thead>
                <tbody>
                  {categoryRows.length === 0 ? (
                    <tr>
                      <td colSpan={4} className="py-10 text-center text-slate-500">
                        No data
                      </td>
                    </tr>
                  ) : (
                    categoryRows.map((r, idx) => (
                      <tr key={r.student_id || r.id || idx} className="border-b border-slate-800/60">
                        <td className="py-2 px-2 text-slate-300">{idx + 1}</td>
                        <td className="py-2 px-2 text-slate-200 font-medium">{r.name || r.student_name || r.student?.name || r.student_email || '-'}</td>
                        <td className="py-2 px-2 text-emerald-200 font-semibold">{r.average_score != null ? r.average_score : r.avg_percentage != null ? r.avg_percentage : '-'}</td>
                        <td className="py-2 px-2 text-slate-200">{r.attempts_count ?? r.attempts ?? '-'}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </div>

      <Toast toast={toast} onClose={() => setToast(null)} />
    </div>
  )
}

