import { Link } from 'react-router-dom'
import Button from '../components/shared/Button'
import { ROUTES } from '../utils/constants'

export default function NotFoundPage() {
  return (
    <div className="min-h-screen bg-[var(--color-background)] flex items-center justify-center px-4">
      <div className="text-center max-w-sm bg-[var(--color-surface)] p-8 rounded-xl border border-[var(--color-border)] shadow-card">
        <div className="w-16 h-16 rounded-xl bg-[var(--color-surface-soft)] flex items-center justify-center mx-auto mb-4 text-3xl">
          🔍
        </div>
        <h1 className="text-4xl font-display font-bold mb-2">404</h1>
        <h2 className="text-base font-bold text-[var(--color-text-primary)] mb-1">Assessment or Page Not Found</h2>
        <p className="text-xs text-[var(--color-text-secondary)] mb-6">
          The link you followed may be incorrect, expired, or relocated to an archived testing session.
        </p>
        <Link to={ROUTES.HOME}>
          <Button fullWidth>Return to Home</Button>
        </Link>
      </div>
    </div>
  )
}
