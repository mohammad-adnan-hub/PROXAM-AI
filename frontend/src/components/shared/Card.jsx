export default function Card({ children, className = '', accent, ...props }) {
  const accentMap = {
    mint: 'bg-[var(--color-mint)]',
    lavender: 'bg-[var(--color-lavender)]',
    peach: 'bg-[var(--color-peach)]',
    pink: 'bg-[var(--color-pink-pastel)]',
    blue: 'bg-[var(--color-blue)]',
    yellow: 'bg-[var(--color-yellow)]',
  }

  const bgClass = accent
    ? accentMap[accent] || 'bg-[var(--color-surface)]'
    : 'bg-[var(--color-surface)]'

  return (
    <div
      className={[
        bgClass,
        'rounded-lg p-6 shadow-card border border-[var(--color-border)]',
        className,
      ]
        .filter(Boolean)
        .join(' ')}
      {...props}
    >
      {children}
    </div>
  )
}
