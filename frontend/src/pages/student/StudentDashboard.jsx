import { Link } from 'react-router-dom'
import AppLayout from '../../components/layout/AppLayout'
import Button from '../../components/shared/Button'
import Card from '../../components/shared/Card'
import { useAuth } from '../../context/AuthContext'
import { ROUTES } from '../../utils/constants'

export default function StudentDashboard() {
  const { user } = useAuth()

  return (
    <AppLayout>
      <div className="space-y-8">
        {/* Header banner */}
        <div>
          <span className="text-xs font-semibold text-[var(--color-text-muted)] uppercase tracking-wider">
            Student Assessment Portal
          </span>
          <h1 className="page-title mt-1">Continue your examination journey</h1>
          <p className="text-[var(--color-text-secondary)] text-sm mt-1">
            Welcome back, {user?.full_name}. Enter your test code below to unlock your active assessment session.
          </p>
        </div>

        {/* Enter test code CTA card */}
        <div className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl p-8 shadow-card flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div className="max-w-xl">
            <span className="inline-block text-[11px] font-bold px-2.5 py-1 rounded-pill bg-[var(--color-mint)] text-[var(--color-text-primary)] mb-2">
              Fast-Pass Direct Access
            </span>
            <h2 className="text-xl font-bold text-[var(--color-text-primary)]">Have a test code from your teacher?</h2>
            <p className="text-xs text-[var(--color-text-secondary)] mt-1.5 leading-relaxed">
              Enter your assigned examination code (e.g. <span className="font-mono font-semibold text-[var(--color-text-primary)]">PXAM-7K4Q2</span>) to load instructions, complete hardware verification, and commence your timed examination.
            </p>
          </div>
          <Link to={ROUTES.STUDENT_ENTER_CODE}>
            <Button size="lg" className="whitespace-nowrap">
              Enter Test Code →
            </Button>
          </Link>
        </div>

        {/* Recent examinations placeholder */}
        <div>
          <h2 className="text-base font-bold mb-4 text-[var(--color-text-primary)]">Your Examination Records</h2>
          <Card className="text-center py-12">
            <div className="w-12 h-12 rounded-xl bg-[var(--color-surface-soft)] flex items-center justify-center mx-auto mb-3 text-xl">
              📝
            </div>
            <h3 className="font-semibold text-sm">No Examination Attempts Yet</h3>
            <p className="text-xs text-[var(--color-text-secondary)] max-w-sm mx-auto mt-1 mb-4">
              When you complete an assessment using a teacher's test code, your verified submission and grade summary will appear here.
            </p>
            <Link to={ROUTES.STUDENT_ENTER_CODE}>
              <Button size="sm" variant="secondary">Enter Test Code</Button>
            </Link>
          </Card>
        </div>
      </div>
    </AppLayout>
  )
}
