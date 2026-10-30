import { Link } from 'react-router-dom'
import { ROUTES } from '../../utils/constants'
import Button from '../../components/shared/Button'

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-[var(--color-background)] flex flex-col">
      <header className="flex items-center justify-between px-8 py-5 border-b border-[var(--color-border)] bg-[var(--color-surface)]">
        <Link to={ROUTES.HOME} className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-[var(--color-primary)] flex items-center justify-center">
            <span className="font-display font-bold text-[var(--color-mint)] text-sm">P</span>
          </div>
          <span className="font-display font-bold text-[var(--color-text-primary)] text-base">Proxam AI</span>
        </Link>
        <div className="flex items-center gap-4">
          <Link to={ROUTES.LOGIN}><Button variant="secondary" size="sm">Sign In</Button></Link>
          <Link to={ROUTES.REGISTER}><Button size="sm">Get Started</Button></Link>
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-6 py-16">
        <h1 className="text-3xl font-display font-bold mb-4">About Proxam AI</h1>
        <p className="text-[var(--color-text-secondary)] text-base mb-8 leading-relaxed">
          Proxam AI is designed to foster a calm, reliable online testing experience for colleges, educators, and candidates.
          We believe proctoring should be transparent and objective rather than intrusive.
        </p>

        <div className="space-y-6">
          <div className="bg-[var(--color-surface)] p-6 rounded-xl border border-[var(--color-border)] shadow-card">
            <h2 className="text-lg font-bold mb-2">Non-Punitive Telemetry</h2>
            <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed">
              Our system captures browser events such as tab switching, camera availability, and presence indicators.
              These are treated strictly as metadata alerts for authorized human review — never automatic cheating verdicts.
            </p>
          </div>

          <div className="bg-[var(--color-surface)] p-6 rounded-xl border border-[var(--color-border)] shadow-card">
            <h2 className="text-lg font-bold mb-2">Privacy-First Architecture</h2>
            <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed">
              No continuous video or audio feeds are stored in cloud storage. Hardware access is verified locally during the pre-exam check.
            </p>
          </div>
        </div>
      </main>
    </div>
  )
}
