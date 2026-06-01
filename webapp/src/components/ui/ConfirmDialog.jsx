import { useEffect, useState } from 'react'

export default function ConfirmDialog({
  open,
  title = 'Confirm',
  message = 'Are you sure?',
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  danger = false,
  onConfirm,
  onCancel,
}) {
  const [mounted, setMounted] = useState(false)

  useEffect(() => setMounted(true), [])
  if (!open) return null

  return (
    <div className="fixed inset-0 z-[120] flex items-center justify-center">
      <button
        className="absolute inset-0 bg-black/60"
        onClick={onCancel}
        aria-label="Close confirmation"
      />
      <div
        className={[
          'relative w-[92%] sm:w-[520px] rounded-2xl border border-slate-800 bg-slate-950 shadow-2xl',
          mounted ? 'animate-[fadeIn_.12s_ease]' : '',
        ].join(' ')}
      >
        <div className="p-5 sm:p-6">
          <div className="text-slate-100 font-semibold text-base">{title}</div>
          <div className="mt-2 text-sm text-slate-300">{message}</div>

          <div className="mt-6 flex items-center justify-end gap-3">
            <button
              className="px-4 py-2 rounded-xl border border-slate-800 text-slate-200 hover:bg-slate-900"
              onClick={onCancel}
            >
              {cancelText}
            </button>
            <button
              className={[
                'px-4 py-2 rounded-xl text-sm font-semibold border',
                danger
                  ? 'bg-rose-600/15 border-rose-500/30 text-rose-200 hover:bg-rose-600/25'
                  : 'bg-blue-600/15 border-blue-500/30 text-blue-200 hover:bg-blue-600/25',
              ].join(' ')}
              onClick={onConfirm}
            >
              {confirmText}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

