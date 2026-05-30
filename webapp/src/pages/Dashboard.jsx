import { useEffect, useState, useCallback } from 'react'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

const EMPTY_FORM = { question: '', option1: '', option2: '', option3: '', option4: '', correct: '1' }
const EMPTY_CAT  = { name: '', description: '' }

function Toast({ message, type = 'info', onClose }) {
  useEffect(() => {
    const t = setTimeout(onClose, 4000)
    return () => clearTimeout(t)
  }, [message, onClose])

  const colors = {
    info:    { bg: '#1e40af', icon: 'ℹ' },
    success: { bg: '#15803d', icon: '✓' },
    error:   { bg: '#b91c1c', icon: '✕' },
  }
  const { bg, icon } = colors[type] || colors.info

  return (
    <div style={{
      position: 'fixed', bottom: 24, right: 24, zIndex: 9999,
      display: 'flex', alignItems: 'center', gap: 12,
      background: bg, color: '#fff',
      padding: '12px 20px', borderRadius: 12,
      boxShadow: '0 8px 32px rgba(0,0,0,0.35)',
      fontSize: 14, fontWeight: 500, maxWidth: 380,
      animation: 'slideUp .25s ease',
    }}>
      <span style={{ fontSize: 18, lineHeight: 1 }}>{icon}</span>
      <span style={{ flex: 1 }}>{message}</span>
      <button onClick={onClose} style={{
        background: 'rgba(255,255,255,.2)', border: 'none', color: '#fff',
        borderRadius: 6, width: 24, height: 24, cursor: 'pointer',
        fontSize: 14, lineHeight: '24px', textAlign: 'center', padding: 0,
      }}>✕</button>
    </div>
  )
}

function StatCard({ label, value, icon, accent }) {
  return (
    <div style={{
      background: '#0f1629', border: `1px solid ${accent}33`,
      borderRadius: 16, padding: '20px 24px',
      display: 'flex', flexDirection: 'column', gap: 8,
      position: 'relative', overflow: 'hidden',
    }}>
      <div style={{
        position: 'absolute', top: -12, right: -12,
        width: 80, height: 80, borderRadius: '50%',
        background: `${accent}18`,
      }} />
      <span style={{ fontSize: 28 }}>{icon}</span>
      <p style={{ margin: 0, fontSize: 13, color: '#94a3b8', fontFamily: 'inherit' }}>{label}</p>
      <p style={{ margin: 0, fontSize: 32, fontWeight: 700, color: '#f1f5f9', fontFamily: 'inherit' }}>{value}</p>
    </div>
  )
}

function Spinner() {
  return (
    <span style={{
      display: 'inline-block', width: 16, height: 16,
      border: '2px solid rgba(255,255,255,.3)',
      borderTopColor: '#fff', borderRadius: '50%',
      animation: 'spin .7s linear infinite',
    }} />
  )
}

export default function Dashboard() {
  const [analytics, setAnalytics]           = useState({ students: 0, quizzes: 0, avg_score: 0 })
  const [quizzes, setQuizzes]               = useState([])
  const [categories, setCategories]         = useState([])
  const [selectedCategory, setSelectedCategory] = useState(null)
  const [categoryForm, setCategoryForm]     = useState(EMPTY_CAT)
  const [form, setForm]                     = useState(EMPTY_FORM)
  const [editingQuizId, setEditingQuizId]   = useState(null)
  const [topStudents, setTopStudents]       = useState([])
  const [showTopStudents, setShowTopStudents] = useState(false)
  const [topStudentsLoading, setTopStudentsLoading] = useState(false)
  const [topStudentsMessage, setTopStudentsMessage] = useState(null)
  const [toast, setToast]                   = useState(null)
  const [loadingQuiz, setLoadingQuiz]       = useState(false)
  const [loadingCategories, setLoadingCategories] = useState(false)
  const [deletingId, setDeletingId]         = useState(null)
  const [activeTab, setActiveTab]           = useState('create')
  const [searchQuery, setSearchQuery]       = useState('')

  const notify = useCallback((msg, type = 'info') => setToast({ msg, type, key: Date.now() }), [])

  const loadAnalytics = async () => {
    try {
      const res  = await fetch(`${API_BASE}/analytics`)
      const data = await res.json()
      setAnalytics(data)
    } catch { notify('Analytics yuklanmadi', 'error') }
  }

  const loadCategories = async () => {
    setLoadingCategories(true)
    try {
      const res  = await fetch(`${API_BASE}/categories`)
      const data = await res.json()
      setCategories(data)
      if (data.length) setSelectedCategory(c => c ?? data[0].id)
    } catch { notify('Kategoriyalar yuklanmadi', 'error') }
    finally { setLoadingCategories(false) }
  }

  const loadQuizzes = useCallback(async (catId) => {
    try {
      const url  = catId ? `${API_BASE}/quizzes?category_id=${catId}` : `${API_BASE}/quizzes`
      const res  = await fetch(url)
      const data = await res.json()
      setQuizzes(data)
    } catch { notify('Quizlar yuklanmadi', 'error') }
  }, [])

  const loadTopStudents = async (categoryId) => {
    if (!categoryId) { setTopStudents([]); return }
    setTopStudentsLoading(true); setTopStudentsMessage(null)
    try {
      const res = await fetch(`${API_BASE}/categories/${categoryId}/top-students`)
      if (!res.ok) {
        const d = await res.json().catch(() => null)
        setTopStudentsMessage(d?.detail || 'Top talabalar yuklanmadi.')
        setTopStudents([]); return
      }
      const data = await res.json()
      setTopStudents(data)
      if (!data.length) setTopStudentsMessage('Bu kategoriyada hali talabalar yo\'q.')
    } catch {
      setTopStudentsMessage('Top talabalar yuklanmadi.')
      setTopStudents([])
    } finally { setTopStudentsLoading(false) }
  }

  useEffect(() => {
    loadAnalytics(); loadCategories(); loadQuizzes()
  }, [])

  useEffect(() => {
    if (selectedCategory !== null) {
      loadQuizzes(selectedCategory)
      if (showTopStudents) loadTopStudents(selectedCategory)
    }
  }, [selectedCategory])

  const handleFormChange = e => {
    const { name, value } = e.target
    setForm(p => ({ ...p, [name]: value }))
  }

  const createCategory = async e => {
    e.preventDefault()
    if (!categoryForm.name.trim()) { notify('Kategoriya nomi kiritilishi shart', 'error'); return }
    try {
      const res = await fetch(`${API_BASE}/categories`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(categoryForm),
      })
      if (!res.ok) {
        const d = await res.json().catch(() => null)
        notify(d?.detail || 'Kategoriya yaratilmadi.', 'error'); return
      }
      const newCat = await res.json()
      setCategoryForm(EMPTY_CAT)
      await loadCategories()
      setSelectedCategory(newCat.id)
      await loadQuizzes(newCat.id)
      notify('Kategoriya muvaffaqiyatli yaratildi!', 'success')
    } catch { notify('Kategoriya yaratilmadi.', 'error') }
  }

  const handleSubmit = async e => {
    e.preventDefault()
    if (!selectedCategory) { notify('Avval kategoriya tanlang yoki yarating.', 'error'); return }
    if (!form.question.trim()) { notify('Savol matnini kiriting.', 'error'); return }
    const opts = [form.option1, form.option2, form.option3, form.option4]
    if (opts.some(o => !o.trim())) { notify('Barcha variantlarni to\'ldiring.', 'error'); return }

    setLoadingQuiz(true)
    try {
      const payload = { ...form, correct: Number(form.correct), category_id: selectedCategory }
      const method  = editingQuizId ? 'PUT'  : 'POST'
      const url     = editingQuizId ? `${API_BASE}/quizzes/${editingQuizId}` : `${API_BASE}/quizzes`
      const res     = await fetch(url, { method, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
      if (!res.ok) {
        const d = await res.json().catch(() => null)
        notify(d?.detail || (editingQuizId ? 'Yangilanmadi.' : 'Saqlanmadi.'), 'error'); return
      }
      setForm(EMPTY_FORM); setEditingQuizId(null)
      notify(editingQuizId ? 'Quiz muvaffaqiyatli yangilandi!' : 'Quiz muvaffaqiyatli saqlandi!', 'success')
      await loadAnalytics(); await loadQuizzes(selectedCategory)
      setActiveTab('list')
    } catch { notify(editingQuizId ? 'Yangilanmadi.' : 'Saqlanmadi.', 'error') }
    finally { setLoadingQuiz(false) }
  }

  const handleDelete = async id => {
    if (!window.confirm('Bu quizni o\'chirishni tasdiqlaysizmi?')) return
    setDeletingId(id)
    try {
      const res = await fetch(`${API_BASE}/quizzes/${id}`, { method: 'DELETE' })
      if (!res.ok) {
        const d = await res.json().catch(() => null)
        notify(d?.detail || 'O\'chirilmadi.', 'error'); return
      }
      notify('Quiz o\'chirildi.', 'success')
      await loadAnalytics(); await loadQuizzes(selectedCategory)
      if (editingQuizId === id) cancelEdit()
    } catch { notify('O\'chirilmadi.', 'error') }
    finally { setDeletingId(null) }
  }

  const cancelEdit = () => {
    setEditingQuizId(null); setForm(EMPTY_FORM)
  }

  const handleEditQuiz = quiz => {
    setForm({
      question: quiz.question,
      option1: quiz.option1, option2: quiz.option2,
      option3: quiz.option3, option4: quiz.option4,
      correct: String(quiz.correct),
    })
    setSelectedCategory(quiz.category_id ?? selectedCategory)
    setEditingQuizId(quiz.id)
    setActiveTab('create')
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const filteredQuizzes = quizzes.filter(q =>
    q.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
    [q.option1, q.option2, q.option3, q.option4].some(o => o.toLowerCase().includes(searchQuery.toLowerCase()))
  )

  const selectedCategoryName = categories.find(c => c.id === selectedCategory)?.name || ''

  const medals = ['🥇', '🥈', '🥉']

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { background: #060d1f; font-family: 'Sora', sans-serif; color: #e2e8f0; min-height: 100vh; }
        @keyframes spin { to { transform: rotate(360deg); } }
        @keyframes slideUp { from { transform: translateY(16px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        @keyframes modalIn { from { transform: scale(.96) translateY(12px); opacity: 0; } to { transform: scale(1) translateY(0); opacity: 1; } }
        input, textarea, select {
          width: 100%; background: #0a1020; border: 1px solid #1e3058;
          color: #e2e8f0; border-radius: 10px; padding: 10px 14px;
          font-family: 'Sora', sans-serif; font-size: 14px; transition: border-color .2s, box-shadow .2s; outline: none;
        }
        input:focus, textarea:focus, select:focus {
          border-color: #3b82f6; box-shadow: 0 0 0 3px rgba(59,130,246,.15);
        }
        input::placeholder, textarea::placeholder { color: #475569; }
        textarea { resize: vertical; min-height: 90px; line-height: 1.6; }
        select option { background: #0a1020; }
        button { font-family: 'Sora', sans-serif; cursor: pointer; }
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: #0a1020; }
        ::-webkit-scrollbar-thumb { background: #1e3058; border-radius: 3px; }
        .btn-primary {
          background: linear-gradient(135deg, #1d4ed8, #2563eb);
          color: #fff; border: none; border-radius: 10px;
          padding: 10px 20px; font-size: 14px; font-weight: 600;
          transition: opacity .2s, transform .1s; display: inline-flex; align-items: center; gap: 8px;
        }
        .btn-primary:hover:not(:disabled) { opacity: .88; transform: translateY(-1px); }
        .btn-primary:active:not(:disabled) { transform: translateY(0); }
        .btn-primary:disabled { opacity: .55; cursor: not-allowed; }
        .btn-secondary {
          background: #1e293b; color: #94a3b8; border: 1px solid #1e3058;
          border-radius: 10px; padding: 10px 20px; font-size: 14px; font-weight: 500;
          transition: background .2s, color .2s;
        }
        .btn-secondary:hover { background: #273449; color: #e2e8f0; }
        .btn-danger {
          background: transparent; color: #f87171; border: 1px solid #7f1d1d55;
          border-radius: 8px; padding: 6px 14px; font-size: 13px; font-weight: 500;
          transition: background .2s;
        }
        .btn-danger:hover { background: #7f1d1d22; }
        .btn-edit {
          background: transparent; color: #60a5fa; border: 1px solid #1e4a8055;
          border-radius: 8px; padding: 6px 14px; font-size: 13px; font-weight: 500;
          transition: background .2s;
        }
        .btn-edit:hover { background: #1e4a8022; }
        .card {
          background: #0c1525; border: 1px solid #1a2d4d; border-radius: 20px; padding: 28px;
        }
        .section-title {
          font-size: 16px; font-weight: 700; color: #f1f5f9; margin-bottom: 20px;
          display: flex; align-items: center; gap: 10px;
        }
        .label-text {
          font-size: 12px; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: .06em; margin-bottom: 6px; display: block;
        }
        .tab-btn {
          padding: 9px 22px; border-radius: 10px; font-size: 14px; font-weight: 600; border: none;
          transition: background .2s, color .2s;
        }
        .tab-active { background: #1d4ed8; color: #fff; }
        .tab-inactive { background: transparent; color: #64748b; }
        .tab-inactive:hover { color: #94a3b8; }
        .quiz-option {
          padding: 8px 14px; border-radius: 8px; font-size: 13.5px;
          background: #0a1020; border: 1px solid #1a2d4d; color: #94a3b8;
          display: flex; align-items: center; gap: 10px;
        }
        .quiz-option.correct {
          border-color: #166534; background: #052e1633; color: #4ade80;
        }
        .opt-badge {
          width: 22px; height: 22px; border-radius: 50%; display: flex; align-items: center; justify-content: center;
          font-size: 11px; font-weight: 700; flex-shrink: 0;
        }
        .search-wrap { position: relative; }
        .search-wrap input { padding-left: 40px; }
        .search-icon { position: absolute; left: 14px; top: 50%; transform: translateY(-50%); color: #475569; font-size: 15px; pointer-events: none; }
        .empty-state { text-align: center; padding: 60px 20px; color: #475569; }
        .empty-state p:first-child { font-size: 40px; margin-bottom: 12px; }
        .empty-state p:last-child { font-size: 14px; }
        .badge {
          display: inline-flex; align-items: center;
          padding: 3px 10px; border-radius: 20px; font-size: 11.5px; font-weight: 600;
        }
        .badge-blue { background: #1e3a5f; color: #60a5fa; }
        .badge-green { background: #052e16; color: #4ade80; }
      `}</style>

      <div style={{ minHeight: '100vh', background: '#060d1f' }}>
        {/* Header */}
        <header style={{
          background: '#0a1020', borderBottom: '1px solid #1a2d4d',
          padding: '0 32px', height: 64,
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          position: 'sticky', top: 0, zIndex: 100,
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
            <div style={{
              width: 36, height: 36, borderRadius: 10,
              background: 'linear-gradient(135deg, #1d4ed8, #7c3aed)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: 18,
            }}>🏛</div>
            <div>
              <p style={{ fontSize: 16, fontWeight: 700, color: '#f1f5f9', lineHeight: 1.2 }}>Registon</p>
              <p style={{ fontSize: 11, color: '#475569', lineHeight: 1 }}>Admin Panel</p>
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span className="badge badge-green">● Online</span>
          </div>
        </header>

        <main style={{ maxWidth: 1200, margin: '0 auto', padding: '32px 24px' }}>
          {/* Stats */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 16, marginBottom: 28 }}>
            <StatCard label="Jami talabalar"  value={analytics.students}                    icon="👨‍🎓" accent="#3b82f6" />
            <StatCard label="Jami savollar"   value={analytics.quizzes}                     icon="📚" accent="#8b5cf6" />
            <StatCard label="O'rtacha ball"   value={`${analytics.avg_score ?? 0}%`}        icon="📊" accent="#10b981" />
          </div>

          {/* Category section */}
          <div className="card" style={{ marginBottom: 24 }}>
            <p className="section-title">📂 Kategoriyalar</p>
            <form onSubmit={createCategory} style={{ display: 'flex', gap: 12, flexWrap: 'wrap', marginBottom: 20 }}>
              <div style={{ flex: '1 1 200px' }}>
                <label className="label-text">Kategoriya nomi</label>
                <input name="name" value={categoryForm.name} onChange={e => setCategoryForm(p => ({...p, name: e.target.value}))} placeholder="Masalan: Matematika" />
              </div>
              <div style={{ flex: '2 1 260px' }}>
                <label className="label-text">Tavsif (ixtiyoriy)</label>
                <input name="description" value={categoryForm.description} onChange={e => setCategoryForm(p => ({...p, description: e.target.value}))} placeholder="Kategoriya haqida qisqacha..." />
              </div>
              <div style={{ display: 'flex', alignItems: 'flex-end' }}>
                <button type="submit" className="btn-primary">
                  <span>+</span> Yaratish
                </button>
              </div>
            </form>

            <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', alignItems: 'flex-end' }}>
              <div style={{ flex: '1 1 260px' }}>
                <label className="label-text">Faol kategoriya</label>
                <select
                  value={selectedCategory || ''}
                  onChange={e => setSelectedCategory(e.target.value ? Number(e.target.value) : null)}
                >
                  <option value="">— Kategoriya tanlang —</option>
                  {categories.map(c => (
                    <option key={c.id} value={c.id}>{c.name}</option>
                  ))}
                </select>
              </div>
              <button
                type="button"
                className="btn-secondary"
                disabled={!selectedCategory}
                onClick={() => { setShowTopStudents(true); loadTopStudents(selectedCategory) }}
                style={{ minWidth: 200, height: 42, display: 'flex', alignItems: 'center', gap: 8, justifyContent: 'center' }}
              >
                🏆 Top 10 talaba
              </button>
            </div>
            {loadingCategories && <p style={{ marginTop: 12, fontSize: 13, color: '#475569' }}>Yuklanmoqda...</p>}
          </div>

          {/* Tabs */}
          <div style={{ display: 'flex', gap: 8, marginBottom: 20 }}>
            {[
              { key: 'create', label: editingQuizId ? '✏️ Tahrirlash' : '➕ Yangi savol' },
              { key: 'list',   label: `📚 Savollar ro'yxati (${quizzes.length})` },
            ].map(tab => (
              <button
                key={tab.key}
                className={`tab-btn ${activeTab === tab.key ? 'tab-active' : 'tab-inactive'}`}
                onClick={() => setActiveTab(tab.key)}
              >{tab.label}</button>
            ))}
          </div>

          {/* Create / Edit form */}
          {activeTab === 'create' && (
            <div className="card" style={{ animation: 'fadeIn .2s ease' }}>
              <p className="section-title">
                {editingQuizId ? '✏️ Savolni tahrirlash' : '➕ Yangi savol qo\'shish'}
                {selectedCategoryName && (
                  <span className="badge badge-blue" style={{ fontSize: 12, marginLeft: 4 }}>{selectedCategoryName}</span>
                )}
              </p>
              <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 18 }}>
                <div>
                  <label className="label-text">Savol matni</label>
                  <textarea name="question" value={form.question} onChange={handleFormChange} placeholder="Savolingizni kiriting..." />
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 14 }}>
                  {[1,2,3,4].map(n => (
                    <div key={n}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 6 }}>
                        <button
                          type="button"
                          onClick={() => setForm(p => ({ ...p, correct: String(n) }))}
                          title={`To'g'ri javob: Variant ${n}`}
                          style={{
                            width: 26, height: 26, borderRadius: '50%',
                            border: `2px solid ${String(n) === form.correct ? '#4ade80' : '#1e3058'}`,
                            background: String(n) === form.correct ? '#052e1630' : '#0a1020',
                            display: 'flex', alignItems: 'center', justifyContent: 'center',
                            cursor: 'pointer',
                          }}
                        >
                          <span style={{ color: String(n) === form.correct ? '#4ade80' : '#64748b', fontSize: 14, lineHeight: 1 }}>
                            {String(n) === form.correct ? '✓' : ' '}
                          </span>
                        </button>

                        <label className="label-text" style={{ marginBottom: 0 }}>
                          Variant {n}
                        </label>

                        {String(n) === form.correct && (
                          <span style={{ marginLeft: 8, color: '#4ade80', fontWeight: 700 }}>✓ To'g'ri</span>
                        )}
                      </div>

                      <input
                        name={`option${n}`}
                        value={form[`option${n}`]}
                        onChange={handleFormChange}
                        placeholder={`${n}-variant...`}
                        style={String(n) === form.correct ? { borderColor: '#166534', background: '#052e1620' } : {}}
                      />
                    </div>
                  ))}
                </div>



                <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', paddingTop: 4 }}>
                  <button type="submit" className="btn-primary" disabled={loadingQuiz} style={{ minWidth: 160 }}>
                    {loadingQuiz ? <><Spinner /> Saqlanmoqda...</> : (editingQuizId ? '✓ Yangilash' : '✓ Saqlash')}
                  </button>
                  {editingQuizId && (
                    <button type="button" className="btn-secondary" onClick={cancelEdit}>✕ Bekor qilish</button>
                  )}
                </div>
              </form>
            </div>
          )}

          {/* Quiz list */}
          {activeTab === 'list' && (
            <div style={{ animation: 'fadeIn .2s ease' }}>
              <div style={{ marginBottom: 16 }}>
                <div className="search-wrap">
                  <span className="search-icon">🔍</span>
                  <input
                    value={searchQuery}
                    onChange={e => setSearchQuery(e.target.value)}
                    placeholder="Savol yoki variantlar bo'yicha qidiring..."
                  />
                </div>
              </div>

              {filteredQuizzes.length === 0 ? (
                <div className="empty-state">
                  <p>{searchQuery ? '🔍' : '📭'}</p>
                  <p>{searchQuery ? 'Hech narsa topilmadi' : 'Bu kategoriyada hali savollar yo\'q'}</p>
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
                  {filteredQuizzes.map((quiz, idx) => (
                    <div key={quiz.id} className="card" style={{ padding: '20px 24px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 16, marginBottom: 16 }}>
                        <div style={{ display: 'flex', gap: 14, alignItems: 'flex-start', flex: 1 }}>
                          <span style={{
                            minWidth: 28, height: 28, borderRadius: 8,
                            background: '#1e3a5f', color: '#60a5fa',
                            display: 'flex', alignItems: 'center', justifyContent: 'center',
                            fontSize: 12, fontWeight: 700, flexShrink: 0, marginTop: 2,
                          }}>{idx + 1}</span>
                          <p style={{ fontSize: 15, fontWeight: 600, color: '#f1f5f9', lineHeight: 1.6 }}>{quiz.question}</p>
                        </div>
                        <div style={{ display: 'flex', gap: 8, flexShrink: 0 }}>
                          <button className="btn-edit" onClick={() => handleEditQuiz(quiz)}>✏️ Tahrirlash</button>
                          <button
                            className="btn-danger"
                            onClick={() => handleDelete(quiz.id)}
                            disabled={deletingId === quiz.id}
                          >
                            {deletingId === quiz.id ? <Spinner /> : '🗑 O\'chirish'}
                          </button>
                        </div>
                      </div>
                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 8 }}>
                        {[1,2,3,4].map(n => (
                          <div key={n} className={`quiz-option ${n === quiz.correct ? 'correct' : ''}`}>
                            <span className="opt-badge" style={{
                              background: n === quiz.correct ? '#166534' : '#1e3058',
                              color: n === quiz.correct ? '#4ade80' : '#64748b',
                            }}>{n}</span>
                            <span>{quiz[`option${n}`]}</span>
                            {n === quiz.correct && <span style={{ marginLeft: 'auto', fontSize: 13 }}>✓</span>}
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </main>
      </div>

      {/* Top Students Modal */}
      {showTopStudents && (
        <div
          style={{
            position: 'fixed', inset: 0, zIndex: 200,
            background: 'rgba(0,0,0,.75)', backdropFilter: 'blur(4px)',
            display: 'flex', justifyContent: 'center', alignItems: 'center',
            padding: 24, animation: 'fadeIn .2s ease',
          }}
          onClick={() => setShowTopStudents(false)}
        >
          <div
            style={{
              background: '#0c1525', borderRadius: 24, border: '1px solid #1a2d4d',
              width: '100%', maxWidth: 700, maxHeight: '88vh', overflowY: 'auto',
              padding: 32, animation: 'modalIn .25s ease',
            }}
            onClick={e => e.stopPropagation()}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 28 }}>
              <div>
                <p style={{ fontSize: 22, fontWeight: 700, color: '#f1f5f9' }}>🏆 Top 10 Talabalar</p>
                <p style={{ fontSize: 14, color: '#60a5fa', marginTop: 4 }}>{selectedCategoryName}</p>
              </div>
              <button
                className="btn-secondary"
                onClick={() => setShowTopStudents(false)}
                style={{ padding: '8px 18px' }}
              >✕ Yopish</button>
            </div>

            {topStudentsLoading ? (
              <div style={{ textAlign: 'center', padding: '60px 0', color: '#475569' }}>
                <div style={{ marginBottom: 12 }}><Spinner /></div>
                <p style={{ fontSize: 14 }}>Yuklanmoqda...</p>
              </div>
            ) : topStudentsMessage ? (
              <div style={{ textAlign: 'center', padding: '60px 0' }}>
                <p style={{ fontSize: 36, marginBottom: 12 }}>📭</p>
                <p style={{ fontSize: 14, color: '#64748b' }}>{topStudentsMessage}</p>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                {topStudents.map((student, i) => (
                  <div key={student.id} style={{
                    display: 'flex', alignItems: 'center', gap: 16,
                    background: i < 3 ? '#0f1f3d' : '#0a1020',
                    border: `1px solid ${i < 3 ? '#1e3a6e' : '#1a2d4d'}`,
                    borderRadius: 14, padding: '14px 20px',
                    transition: 'background .2s',
                  }}>
                    <span style={{ fontSize: i < 3 ? 28 : 18, minWidth: 36, textAlign: 'center' }}>
                      {i < 3 ? medals[i] : `#${i+1}`}
                    </span>
                    <div style={{
                      width: 42, height: 42, borderRadius: '50%', flexShrink: 0,
                      background: 'linear-gradient(135deg, #1d4ed8, #7c3aed)',
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      color: '#fff', fontWeight: 700, fontSize: 15,
                    }}>
                      {student.name?.[0]?.toUpperCase() || '?'}
                    </div>
                    <div style={{ flex: 1 }}>
                      <p style={{ fontSize: 15, fontWeight: 600, color: '#f1f5f9' }}>{student.name}</p>
                      <p style={{ fontSize: 12, color: '#64748b', marginTop: 2, fontFamily: 'JetBrains Mono, monospace' }}>{student.email}</p>
                    </div>
                    <div style={{
                      background: i === 0 ? '#713f12' : i === 1 ? '#1e3a5f' : '#052e16',
                      color:      i === 0 ? '#fbbf24' : i === 1 ? '#60a5fa' : '#4ade80',
                      borderRadius: 10, padding: '6px 16px', fontWeight: 700, fontSize: 15,
                    }}>
                      {student.score}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Toast */}
      {toast && (
        <Toast
          key={toast.key}
          message={toast.msg}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}
    </>
  )
}