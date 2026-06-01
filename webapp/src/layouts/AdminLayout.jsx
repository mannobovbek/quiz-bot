import { useMemo, useState, useEffect } from 'react'
import { NavLink, Outlet, useLocation } from 'react-router-dom'

function HamburgerIcon({ open }) {
  return (
    <span aria-hidden className="inline-flex items-center">
      {open ? '✕' : '☰'}
    </span>
  )
}

export default function AdminLayout({ children }) {
  const location = useLocation()
  const [mobileOpen, setMobileOpen] = useState(false)

  const navItems = useMemo(
    () => [
      { to: '/', label: 'Dashboard' },
      { to: '/quizzes', label: 'Quiz List' },
      { to: '/students', label: 'Students' },
      { to: '/leaderboard', label: 'Leaderboard' },
      { to: '/excel', label: 'Excel' },
    ],
    []
  )

  useEffect(() => {
    // Close sidebar after navigation on mobile
    setMobileOpen(false)
  }, [location.pathname])

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      {/* Top Navbar */}
      <header className="sticky top-0 z-40 border-b border-slate-800 bg-slate-950">
        <div className="h-16 px-4 sm:px-6 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              className="sm:hidden inline-flex items-center justify-center w-10 h-10 rounded-md border border-slate-800 bg-slate-900"
              onClick={() => setMobileOpen((v) => !v)}
              aria-label="Open menu"
            >
              <HamburgerIcon open={mobileOpen} />
            </button>

            <div className="flex flex-col leading-tight">
              <span className="text-base font-bold">Registon</span>
              <span className="text-xs text-slate-400">Admin Panel</span>
            </div>
          </div>

          <div className="hidden sm:flex items-center gap-3 text-sm text-emerald-400">
            <span className="inline-flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-400" /> Online
            </span>
          </div>

          <div className="sm:hidden text-xs text-slate-400">Online</div>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar (desktop) */}
        <aside className="hidden sm:flex w-64 flex-shrink-0 border-r border-slate-800 bg-slate-950">
          <div className="p-4 w-full">
            <nav className="flex flex-col gap-2">
              {navItems.map((it) => (
                <NavLink
                  key={it.to}
                  to={it.to}
                  end={it.to === '/'}
                  className={({ isActive }) =>
                    [
                      'px-3 py-2 rounded-md border text-sm font-medium',
                      isActive
                        ? 'bg-blue-600/20 border-blue-500/30 text-blue-200'
                        : 'border-transparent hover:border-slate-800 hover:bg-slate-900/60 text-slate-200',
                    ].join(' ')
                  }
                >
                  {it.label}
                </NavLink>
              ))}
            </nav>
          </div>
        </aside>

        {/* Sidebar (mobile drawer) */}
        {mobileOpen && (
          <div
            className="fixed inset-0 z-50 sm:hidden"
            aria-modal="true"
            role="dialog"
          >
            <button
              className="absolute inset-0 bg-black/60"
              onClick={() => setMobileOpen(false)}
              aria-label="Close menu"
            />
            <aside className="absolute left-0 top-0 bottom-0 w-72 border-r border-slate-800 bg-slate-950">
              <div className="p-4">
                <nav className="flex flex-col gap-2">
                  {navItems.map((it) => (
                    <NavLink
                      key={it.to}
                      to={it.to}
                      end={it.to === '/'}
                      onClick={() => setMobileOpen(false)}
                      className={({ isActive }) =>
                        [
                          'px-3 py-2 rounded-md border text-sm font-medium',
                          isActive
                            ? 'bg-blue-600/20 border-blue-500/30 text-blue-200'
                            : 'border-transparent hover:border-slate-800 hover:bg-slate-900/60 text-slate-200',
                        ].join(' ')
                      }
                    >
                      {it.label}
                    </NavLink>
                  ))}
                </nav>
              </div>
            </aside>
          </div>
        )}

        {/* Main */}
        <main className="flex-1 px-4 sm:px-6 py-6">
          {children || <Outlet />}
        </main>
      </div>
    </div>
  )
}

