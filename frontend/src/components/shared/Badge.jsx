const variants = {
  default: 'bg-[var(--color-surface-soft)] text-[var(--color-text-secondary)]',
  success: 'bg-[var(--color-success)] text-[var(--color-text-primary)]',
  warning: 'bg-[var(--color-warning)] text-[var(--color-text-primary)]',
  danger: 'bg-[var(--color-danger)] text-[var(--color-text-primary)]',
  info: 'bg-[var(--color-info)] text-[var(--color-text-primary)]',
  mint: 'bg-[var(--color-mint)] text-[var(--color-text-primary)]',
  lavender: 'bg-[var(--color-lavender)] text-[var(--color-text-primary)]',
  peach: 'bg-[var(--color-peach)] text-[var(--color-text-primary)]',
}

export default function Badge({ children, variant = 'default', className = '' }) {
  return (
    <span
      className={[
        'inline-flex items-center gap-1 px-2.5 py-1 rounded-pill text-xs font-medium',
        variants[variant],
        className,
      ]
        .filter(Boolean)
        .join(' ')}
    >
      {children}
    </span>
  )
}
