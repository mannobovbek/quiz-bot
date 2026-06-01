import { useEffect, useMemo, useState } from 'react'
import { api } from '../services/api'
import Spinner from '../components/Spinner'
import Toast from '../components/Toast'

export default function Students() {
  const [loadingList, setLoadingList] = useState(true)
  const [students, setStudents] = useState([])
  const [selectedId, setSelectedId] = useState(null)

  const [profileLoading, setProfileLoading] = useState(false)
  const [profile, setProfile] = useState(null)

  const [toast, setToast] = useState(null)
  const notify = (message, type = 'info') => setToast({ type, message, duration: 4500 })

  const [listError, setListError] = useState(null)

  useEffect(() => {
    let mounted = true
    ;(async () => {
      setLoadingList(true)
      setListError(null)
      try {
        const res = await api.get('/students')
        if (!mounted) return
        setStudents(res.data || [])
        if (res.data?.length) setSelectedId(res.data[0].id)
      } catch (e) {
        if (!mounted) return
        setListError(e?.normalizedMessage || 'Failed to load students')
        notify(e?.normalizedMessage || 'Failed to load students', 'error')
      } finally {
        if (mounted) setLoadingList(false)
      }
    })()
    return () => {
      mounted = false
    }
  }, [])

  useEffect(() => {
    if (!selectedId) return
    let mounted = true
    ;(async () => {
      setProfileLoading(true)
      setProfile(null)
      try {
        const res = await api.get(`/v2/students/${selectedId}/profile`)
        if (!mounted) return
        setProfile(res.data)
      } catch (e) {
        if (!mounted) return
        notify(e?.normalizedMessage || 'Failed to load student profile', 'error')
      } finally {
        if (mounted) setProfileLoading(false)
      }
    })()
    return () => {
      mounted = false
    }
  }, [selectedId])

  const recentAttempts = useMemo(() => {
    return profile?.recent_attempts || []
  }, [profile])

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-bold">Students</h1>
        <div className="text-sm text-slate-400 mt-1">List, profile and statistics</div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">
        <section className="xl:col-span-1 rounded-2xl border border-slate-800 bg-slate-900/30 p-4">
          <div className="text-sm font-semibold">All Students</div>
          {loadingList ? (
            <div className="mt-4 flex items-center gap-3 text-slate-300">
              <Spinner className="w-6 h-6" />
              Loading...
            </div>
          ) : listError ? (
            <div className="mt-4 rounded-xl border border-rose-500/30 bg-rose-500/10 text-rose-200 p-4">{listError}</div>
          ) : (
            <div className="mt-4 space-y-2 max-h-[520px] overflow-auto pr-1">
              {students.map((s) => (
                <button
                  key={s.id}
                  className={[
                    'w-full text-left rounded-xl border px-3 py-2',
                    selectedId === s.id
                      ? 'border-blue-500/40 bg-blue-600/15 text-blue-100'
                      : 'border-slate-800 bg-slate-950/20 text-slate-200 hover:bg-slate-900',
                  ].join(' ')}
                  onClick={() => setSelectedId(s.id)}
                >
                  <div className="font-medium">{s.name || '—'}</div>
                  <div className="text-xs text-slate-400 truncate">{s.email || ''}</div>
                </button>
              ))}
              {students.length === 0 && (
                <div className="text-slate-500 text-sm py-10 text-center">No students</div>
              )}
            </div>
          )}
        </section>

        <section className="xl:col-span-2 rounded-2xl border border-slate-800 bg-slate-900/30 p-4">
          {!selectedId ? (
            <div className="text-slate-500">Select a student.</div>
          ) : profileLoading ? (
            <div className="flex items-center gap-3 text-slate-300">
              <Spinner className="w-6 h-6" />
              Loading profile...
            </div>
          ) : profile ? (
            <div className="space-y-4">
              <div>
                <div className="text-sm text-slate-400">Student Profile</div>
                <div className="text-xl font-bold">{profile.name || '—'}</div>
                <div className="text-sm text-slate-400">{profile.email || ''}</div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                <div className="rounded-xl border border-slate-800 bg-slate-950/20 p-4">
                  <div className="text-xs text-slate-400">Total Score</div>
                  <div className="text-2xl font-bold">{profile.score ?? 0}</div>
                </div>
                <div className="rounded-xl border border-slate-800 bg-slate-950/20 p-4">
                  <div className="text-xs text-slate-400">Attempts Count</div>
                  <div className="text-2xl font-bold">{profile.attempts_count ?? profile.attempts ?? 0}</div>
                </div>
                <div className="rounded-xl border border-slate-800 bg-slate-950/20 p-4">
                  <div className="text-xs text-slate-400">Average %</div>
                  <div className="text-2xl font-bold">{profile.avg_percentage ?? profile.avg_score ?? 0}%</div>
                </div>
              </div>

              <div className="rounded-2xl border border-slate-800 bg-slate-950/20 p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-sm font-semibold">Recent Attempts</div>
                    <div className="text-xs text-slate-400">Latest finished attempts</div>
                  </div>
                </div>

                <div className="mt-4 overflow-x-auto">
                  <table className="min-w-[820px] w-full text-sm">
                    <thead className="text-slate-400">
                      <tr className="text-left border-b border-slate-800">
                        <th className="py-2 px-2">Quiz</th>
                        <th className="py-2 px-2">Score</th>
                        <th className="py-2 px-2">Percentage</th>
                        <th className="py-2 px-2">Duration (min)</th>
                        <th className="py-2 px-2">Submitted</th>
                      </tr>
                    </thead>
                    <tbody>
                      {recentAttempts.length === 0 ? (
                        <tr>
                          <td colSpan={5} className="py-10 text-center text-slate-500">No attempts yet</td>
                        </tr>
                      ) : (
                        recentAttempts.map((a, idx) => (
                          <tr key={a.attempt_id || idx} className="border-b border-slate-800/60">
                            <td className="py-2 px-2 text-slate-200">{a.quiz_name || '-'}</td>
                            <td className="py-2 px-2 text-emerald-200 font-semibold">{a.score ?? 0}</td>
                            <td className="py-2 px-2 text-slate-200">{a.percentage != null ? `${a.percentage}%` : '-'}</td>
                            <td className="py-2 px-2 text-slate-200">{a.duration_minutes ?? 0}</td>
                            <td className="py-2 px-2 text-slate-400">{a.submitted_at ? String(a.submitted_at).slice(0, 19) : '-'}</td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-slate-500">No profile data.</div>
          )}
        </section>
      </div>

      <Toast toast={toast} onClose={() => setToast(null)} />
    </div>
  )
}

