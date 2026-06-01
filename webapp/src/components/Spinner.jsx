export default function Spinner({ className = 'w-5 h-5' }) {
  return (
    <span
      className={[
        className,
        'inline-block rounded-full border-2 border-slate-600 border-t-slate-100 animate-spin',
      ].join(' ')}
      aria-label="Loading"
    />
  )
}

