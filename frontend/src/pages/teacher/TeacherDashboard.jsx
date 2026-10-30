import { Link } from 'react-router-dom'
import AppLayout from '../../components/layout/AppLayout'
import Button from '../../components/shared/Button'
import Card from '../../components/shared/Card'
import { useAuth } from '../../context/AuthContext'
import { ROUTES } from '../../utils/constants'

export default function TeacherDashboard() {
  const { user } = useAuth()

  return (
    <AppLayout>
      <div className="space-y-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <span className="text-xs font-semibold text-[var(--color-text-muted)] uppercase tracking-wider">
              Faculty Studio
            </span>
            <h1 className="page-title mt-1">Manage your examinations</h1>
            <p className="text-[var(--color-text-secondary)] text-sm mt-1">
              Author proctored assessments, distribute generated codes, and review submission telemetry.
            </p>
          </div>
          <Link to={ROUTES.TEACHER_CREATE_DETAILS}>
            <Button size="lg">+ Create New Test</Button>
          </Link>
        </div>

        {/* Overview metric cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card accent="mint">
            <span className="text-xs font-semibold text-[var(--color-text-secondary)] uppercase">Tests Created</span>
            <p className="text-3xl font-display font-extrabold mt-2">0</p>
            <p className="text-xs text-[var(--color-text-secondary)] mt-1">Active assessments</p>
          </Card>
          <Card accent="lavender">
            <span className="text-xs font-semibold text-[var(--color-text-secondary)] uppercase">Total Submissions</span>
            <p className="text-3xl font-display font-extrabold mt-2">0</p>
            <p className="text-xs text-[var(--color-text-secondary)] mt-1">Candidate attempts evaluated</p>
          </Card>
          <Card accent="peach">
            <span className="text-xs font-semibold text-[var(--color-text-secondary)] uppercase">Pending Reviews</span>
            <p className="text-3xl font-display font-extrabold mt-2">0</p>
            <p className="text-xs text-[var(--color-text-secondary)] mt-1">Telemetry alerts requiring check</p>
          </Card>
        </div>

        {/* Test records table card */}
        <div>
          <h2 className="text-base font-bold mb-4 text-[var(--color-text-primary)]">Your Created Tests</h2>
          <Card className="text-center py-12">
            <div className="w-12 h-12 rounded-xl bg-[var(--color-surface-soft)] flex items-center justify-center mx-auto mb-3 text-xl">
              📂
            </div>
            <h3 className="font-semibold text-sm">No Examinations Authored Yet</h3>
            <p className="text-xs text-[var(--color-text-secondary)] max-w-sm mx-auto mt-1 mb-4">
              Get started by creating your first multiple-choice assessment. Proxam AI will generate a unique 10-character code automatically.
            </p>
            <Link to={ROUTES.TEACHER_CREATE_DETAILS}>
              <Button size="sm">Create First Examination</Button>
            </Link>
          </Card>
        </div>
      </div>
    </AppLayout>
  )
}
