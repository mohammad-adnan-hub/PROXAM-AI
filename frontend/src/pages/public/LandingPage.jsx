import { Link } from 'react-router-dom'
import { ROUTES } from '../../utils/constants'
import Button from '../../components/shared/Button'

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-[var(--color-background)] flex flex-col">
      {/* Header */}
      <header className="flex items-center justify-between px-8 py-5 border-b border-[var(--color-border)] bg-[var(--color-surface)]">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-[var(--color-primary)] flex items-center justify-center">
            <span className="font-display font-bold text-[var(--color-mint)] text-sm">P</span>
          </div>
          <span className="font-display font-bold text-[var(--color-text-primary)] text-base">Proxam AI</span>
        </div>
        <nav className="flex items-center gap-5">
          <Link to={ROUTES.ABOUT} className="text-sm font-medium text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] transition-colors">
            About
          </Link>
          <Link to={ROUTES.HELP} className="text-sm font-medium text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] transition-colors">
            Help & FAQ
          </Link>
          <Link to={ROUTES.LOGIN}>
            <Button variant="secondary" size="sm">Sign In</Button>
          </Link>
          <Link to={ROUTES.REGISTER}>
            <Button size="sm">Get Started</Button>
          </Link>
        </nav>
      </header>

      {/* Hero */}
      <section className="max-w-4xl mx-auto px-6 py-20 text-center">
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-pill bg-[var(--color-mint)]/40 border border-[var(--color-mint)] text-xs font-semibold mb-6">
          <span>●</span> Browser-Based Proctored Assessments
        </div>
        <h1 className="page-title mb-6">
          Fair, calm examinations.<br />
          <span className="text-[var(--color-text-secondary)]">Powered by transparent AI.</span>
        </h1>
        <p className="text-base md:text-lg text-[var(--color-text-secondary)] max-w-2xl mx-auto mb-10">
          Proxam AI helps teachers author MCQ examinations and students attempt them securely with browser-level proctoring.
          Suspicious signals are recorded as transparent metadata for human review — never automated disqualifications.
        </p>
        <div className="flex items-center justify-center gap-4 flex-wrap">
          <Link to={ROUTES.REGISTER}>
            <Button size="lg">Create Free Account →</Button>
          </Link>
          <Link to={ROUTES.LOGIN}>
            <Button variant="secondary" size="lg">Enter Workspace</Button>
          </Link>
        </div>
      </section>

      {/* Feature cards */}
      <section className="max-w-5xl mx-auto px-6 pb-20 w-full">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="rounded-xl p-6 border border-[var(--color-border)] bg-[var(--color-mint)]/30">
            <span className="text-2xl mb-3 block">🎓</span>
            <h3 className="text-base font-bold mb-2 text-[var(--color-text-primary)]">For Students</h3>
            <p className="text-sm text-[var(--color-text-secondary)]">
              Enter a unique test code, complete system pre-checks, and attempt exams in an intuitive, distraction-free environment.
            </p>
          </div>
          <div className="rounded-xl p-6 border border-[var(--color-border)] bg-[var(--color-lavender)]/30">
            <span className="text-2xl mb-3 block">👩‍🏫</span>
            <h3 className="text-base font-bold mb-2 text-[var(--color-text-primary)]">For Teachers</h3>
            <p className="text-sm text-[var(--color-text-secondary)]">
              Draft MCQ exams in 3 steps, distribute 10-character codes, and inspect objective response metrics and proctoring timelines.
            </p>
          </div>
          <div className="rounded-xl p-6 border border-[var(--color-border)] bg-[var(--color-peach)]/30">
            <span className="text-2xl mb-3 block">🛡️</span>
            <h3 className="text-base font-bold mb-2 text-[var(--color-text-primary)]">Auditable Proctoring</h3>
            <p className="text-sm text-[var(--color-text-secondary)]">
              No continuous webcam or mic storage. Metadata events provide contextual evidence for human decision-making.
            </p>
          </div>
        </div>
      </section>

      <footer className="mt-auto border-t border-[var(--color-border)] py-8 text-center text-xs text-[var(--color-text-muted)] bg-[var(--color-surface)]">
        © {new Date().getFullYear()} Proxam AI. All rights reserved.
      </footer>
    </div>
  )
}
