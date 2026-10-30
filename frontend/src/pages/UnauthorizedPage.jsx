import { Link } from 'react-router-dom'
import Button from '../components/shared/Button'
import { ROUTES } from '../utils/constants'

export default function UnauthorizedPage() {
  return (
    <div className="min-h-screen bg-[var(--color-background)] flex items-center justify-center px-4">
      <div className="text-center max-w-sm bg-[var(--color-surface)] p-8 rounded-xl border border-[var(--color-border)] shadow-card">
        <div className="w-16 h-16 rounded-xl bg-[var(--color-surface-soft)] flex items-center justify-center mx-auto mb-4 text-3xl">
          🔒
        </div>
        <h1 className="text-2xl font-display font-bold mb-2">Restricted Access</h1>
        <p className="text-xs text-[var(--color-text-secondary)] mb-6">
          You do not have permission to view this section. Role privileges are enforced for verified faculty, candidates, or administrators.
        </p>
        <Link to={ROUTES.HOME}>
          <Button fullWidth>Back to Workspace</Button>
        </Link>
      </div>
    </div>
  )
}
