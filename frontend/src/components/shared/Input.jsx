import { forwardRef } from 'react'

const Input = forwardRef(function Input(
  { label, error, helperText, className = '', ...props },
  ref
) {
  const id = props.id || props.name
  return (
    <div className="flex flex-col gap-1.5 w-full">
      {label && (
        <label
          htmlFor={id}
          className="text-sm font-medium text-[var(--color-text-primary)]"
        >
          {label}
          {props.required && <span className="text-[var(--color-danger)] ml-0.5">*</span>}
        </label>
      )}
      <input
        ref={ref}
        id={id}
        className={[
          'w-full min-h-[52px] px-4 rounded-md border bg-[var(--color-surface)]',
          'text-[var(--color-text-primary)] placeholder:text-[var(--color-text-muted)]',
          'transition-colors duration-150',
          'focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent',
          error
            ? 'border-[var(--color-danger)]'
            : 'border-[var(--color-border)] hover:border-[var(--color-border-strong)]',
          className,
        ]
          .filter(Boolean)
          .join(' ')}
        {...props}
      />
      {error && (
        <p className="text-xs text-[var(--color-danger)] mt-0.5">{error}</p>
      )}
      {!error && helperText && (
        <p className="text-xs text-[var(--color-text-muted)] mt-0.5">{helperText}</p>
      )}
    </div>
  )
})

export default Input
