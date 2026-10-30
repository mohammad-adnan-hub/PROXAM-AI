import { Link } from 'react-router-dom'
import { ROUTES } from '../../utils/constants'

export default function AuthLayout({ children }) {
  return (
    <div className="min-h-screen bg-[var(--color-background)] flex flex-col">
      <header className="flex items-center justify-between px-8 py-5 border-b border-[var(--color-border)]/50">
        <Link to={ROUTES.HOME} className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-[var(--color-primary)] flex items-center justify-center">
            <span className="font-display font-bold text-[var(--color-mint)] text-sm">P</span>
          </div>
          <span className="font-display font-bold text-[var(--color-text-primary)] text-base">Proxam AI</span>
        </Link>
        <Link
          to={ROUTES.HOME}
          className="text-sm font-medium text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] transition-colors"
        >
          ← Back to Home
        </Link>
      </header>

      <main className="flex-1 flex items-center justify-center px-4 py-10">
        <div className="w-full max-w-md">{children}</div>
      </main>

      <footer className="text-center py-6 text-xs text-[var(--color-text-muted)]">
        © {new Date().getFullYear()} Proxam AI. All rights reserved.
      </footer>
    </div>
  )
}
