import { useEffect } from 'react'

export default function Toast({ toast, onClose }) {
  useEffect(() => {
    if (!toast) return
    const t = setTimeout(() => onClose?.(), toast.duration ?? 4000)
    return () => clearTimeout(t)
  }, [toast, onClose])

  if (!toast) return null

  const colors =
    toast.type === 'success'
      ? {
          border: 'border-emerald-500/30',
          bg: 'bg-emerald-500/10',
          text: 'text-emerald-200',
        }
      : toast.type === 'error'
        ? {
            border: 'border-rose-500/30',
            bg: 'bg-rose-500/10',
            text: 'text-rose-200',
          }
        : {
            border: 'border-blue-500/30',
            bg: 'bg-blue-500/10',
            text: 'text-blue-200',
          }

  return (
    <div className="fixed z-[100] bottom-4 right-4 w-[92%] sm:w-[420px]">
      <div
        className={[
          'rounded-xl border px-4 py-3 shadow-lg',
          colors.border,
          colors.bg,
          colors.text,
        ].join(' ')}
        role="status"
        aria-live="polite"
      >
        <div className="flex items-start gap-3">
          <div className="text-lg leading-none mt-0.5">
            {toast.type === 'success' ? '✓' : toast.type === 'error' ? '✕' : 'ℹ'}
          </div>
          <div className="flex-1 text-sm font-medium">
            {toast.message || toast.msg || ''}
          </div>
          <button
            className="text-slate-300 hover:text-white"
            onClick={() => onClose?.()}
            aria-label="Close"
          >
            ✕
          </button>
        </div>
      </div>
    </div>
  )
}

