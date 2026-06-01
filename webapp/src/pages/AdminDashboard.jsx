import { useEffect, useMemo, useState } from 'react'
import { api } from '../services/api'
import Spinner from '../components/Spinner'
import Toast from '../components/Toast'

function StatCard({ label, value }) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/30 p-4">
      <div className="text-xs uppercase tracking-wide text-slate-400">{label}</div>
      <div className="mt-2 text-2xl font-bold">{value}</div>
    </div>
  )
}

export default function AdminDashboard() {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [toast, setToast] = useState(null)

  const [metrics, setMetrics] = useState({
    students: 0,
    quizzes: 0,
    attempts: 0,
    avg_score: 0,
    recent_attempts: [],
  })

  const showToast = (message, type = 'info') => {
    setToast({ type, message, duration: 4500 })
  }

  useEffect(() => {
    let mounted = true
    ;(async () => {
      setLoading(true)
      setError(null)
      try {
        const res = await api.get('/v2/admin/analytics')
        if (!mounted) return
        setMetrics((p) => ({
          ...p,
          ...res.data,
        }))
      } catch (e) {
        if (!mounted) return
        setError(e?.normalizedMessage || 'Failed to load analytics')
        showToast(e?.normalizedMessage || 'Failed to load analytics', 'error')
      } finally {
        if (mounted) setLoading(false)
      }
    })()
    return () => {
      mounted = false
    }
  }, [])

  const recentRows = useMemo(() => {
    return Array.isArray(metrics.recent_attempts) ? metrics.recent_attempts : []
  }, [metrics.recent_attempts])

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <div className="text-sm text-slate-400 mt-1">Admin overview</div>
      </div>

      {loading ? (
        <div className="flex items-center gap-3 text-slate-300">
          <Spinner className="w-6 h-6" />
          Loading dashboard...
        </div>
      ) : error ? (
        <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 text-rose-200 p-4">
          {error}
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            <StatCard label="Total Students" value={metrics.students ?? 0} />
            <StatCard label="Total Quizzes" value={metrics.quizzes ?? 0} />
            <StatCard label="Total Attempts" value={metrics.attempts ?? metrics.total_attempts ?? 0} />
            <StatCard label="Average Score" value={`${metrics.avg_score ?? 0}%`} />
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900/30 p-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm font-semibold">Recent Attempts</div>
                <div className="text-xs text-slate-400">Latest submissions</div>
              </div>
            </div>

            <div className="mt-4 overflow-x-auto">
              <table className="min-w-[780px] w-full text-sm">
                <thead className="text-slate-400">
                  <tr className="text-left border-b border-slate-800">
                    <th className="py-2 px-2">#</th>
                    <th className="py-2 px-2">Student</th>
                    <th className="py-2 px-2">Quiz</th>
                    <th className="py-2 px-2">Score</th>
                    <th className="py-2 px-2">Percentage</th>
                    <th className="py-2 px-2">Submitted</th>
                  </tr>
                </thead>
                <tbody>
                  {recentRows.length === 0 ? (
                    <tr>
                      <td colSpan={6} className="py-8 text-center text-slate-500">
                        No attempts yet.
                      </td>
                    </tr>
                  ) : (
                    recentRows.map((r, idx) => (
                      <tr key={r.attempt_id || r.id || idx} className="border-b border-slate-800/60">
                        <td className="py-2 px-2 text-slate-300">{idx + 1}</td>
                        <td className="py-2 px-2">
                          <div className="text-slate-200 font-medium">{r.student_email || r.student?.email || r.student || '-'}</div>
                        </td>
                        <td className="py-2 px-2 text-slate-200">{r.quiz_name || r.quiz_title || r.quiz?.title || '-'}</td>
                        <td className="py-2 px-2 text-emerald-200 font-semibold">{r.score ?? 0}</td>
                        <td className="py-2 px-2 text-slate-200">{r.percentage != null ? `${r.percentage}%` : '-'}</td>
                        <td className="py-2 px-2 text-slate-400">{r.submitted_at || r.finished_at || r.started_at || '-'}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}

      <Toast toast={toast} onClose={() => setToast(null)} />
    </div>
  )
}

