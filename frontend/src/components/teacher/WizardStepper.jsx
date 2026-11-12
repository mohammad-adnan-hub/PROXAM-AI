import { Link } from 'react-router-dom'
import { ROUTES } from '../../utils/constants'

const STEPS = [
  { n: 1, label: 'Test Details', to: ROUTES.TEACHER_CREATE_DETAILS },
  { n: 2, label: 'Add MCQ Questions', to: ROUTES.TEACHER_CREATE_QUESTIONS },
  { n: 3, label: 'Preview & Launch', to: ROUTES.TEACHER_CREATE_PREVIEW },
]

export default function WizardStepper({ current = 1 }) {
  const progress = current === 1 ? '33%' : current === 2 ? '66%' : '100%'

  return (
    <div className="bg-[var(--color-surface)] rounded-lg p-4 sm:p-5 shadow-card border border-[var(--color-border)]">
      <div className="grid grid-cols-3 gap-2 sm:gap-4">
        {STEPS.map((step) => {
          const active = step.n === current
          const done = step.n < current
          return (
            <Link
              key={step.n}
              to={step.to}
              className={`flex items-center gap-3 min-w-0 ${active ? '' : 'opacity-70 hover:opacity-100'}`}
            >
              <div
                className={[
                  'w-9 h-9 rounded-full flex items-center justify-center text-sm font-semibold shrink-0',
                  done || active
                    ? 'bg-[var(--color-mint)] text-[var(--color-text-primary)]'
                    : 'bg-[var(--color-surface-soft)] text-[var(--color-text-muted)]',
                ].join(' ')}
              >
                {done ? '✓' : String(step.n).padStart(2, '0')}
              </div>
              <div className="flex flex-col min-w-0">
                <span className="text-sm font-semibold truncate text-[var(--color-text-primary)]">
                  {step.label}
                </span>
                <span className="text-[11px] text-[var(--color-text-muted)] truncate">
                  {active ? 'In progress' : done ? 'Completed' : 'Upcoming'}
                </span>
              </div>
            </Link>
          )
        })}
      </div>
      <div className="w-full bg-[var(--color-surface-soft)] h-1.5 rounded-pill mt-4 overflow-hidden">
        <div
          className="bg-[var(--color-primary)] h-full rounded-pill transition-all duration-300"
          style={{ width: progress }}
        />
      </div>
    </div>
  )
}
