import { Link } from 'react-router-dom'
import AppLayout from '../../components/layout/AppLayout'
import Button from '../../components/shared/Button'
import Card from '../../components/shared/Card'
import { useAuth } from '../../context/AuthContext'
import { ROUTES } from '../../utils/constants'

export default function AdminDashboard() {
  const { user } = useAuth()

  return (
    <AppLayout>
      <div className="space-y-8">
        <div>
          <span className="text-xs font-semibold text-[var(--color-text-muted)] uppercase tracking-wider">
            System Administration
          </span>
          <h1 className="page-title mt-1">Platform Overview</h1>
          <p className="text-[var(--color-text-secondary)] text-sm mt-1">
            Global institution metrics, user roster management, and proctoring telemetry audit.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card accent="mint">
            <span className="text-xs font-semibold text-[var(--color-text-secondary)] uppercase">Users</span>
            <p className="text-2xl font-bold mt-1">Active</p>
            <Link to={ROUTES.ADMIN_USERS} className="text-xs font-semibold text-[var(--color-text-primary)] hover:underline mt-2 block">
              Manage Users →
            </Link>
          </Card>
          <Card accent="lavender">
            <span className="text-xs font-semibold text-[var(--color-text-secondary)] uppercase">Tests</span>
            <p className="text-2xl font-bold mt-1">Managed</p>
            <Link to={ROUTES.ADMIN_TESTS} className="text-xs font-semibold text-[var(--color-text-primary)] hover:underline mt-2 block">
              Manage Tests →
            </Link>
          </Card>
          <Card accent="peach">
            <span className="text-xs font-semibold text-[var(--color-text-secondary)] uppercase">Alerts</span>
            <p className="text-2xl font-bold mt-1">Auditable</p>
            <Link to={ROUTES.ADMIN_PROCTORING} className="text-xs font-semibold text-[var(--color-text-primary)] hover:underline mt-2 block">
              View Alerts →
            </Link>
          </Card>
          <Card accent="blue">
            <span className="text-xs font-semibold text-[var(--color-text-secondary)] uppercase">Security</span>
            <p className="text-2xl font-bold mt-1">Nominal</p>
            <span className="text-xs text-[var(--color-text-muted)] mt-2 block">Role-Based Access</span>
          </Card>
        </div>

        <Card className="p-6">
          <h2 className="text-base font-bold mb-2">Platform Administration Policy</h2>
          <p className="text-xs text-[var(--color-text-secondary)] leading-relaxed">
            In Proxam AI v1, administrators hold authority to audit examinations, inspect proctoring alert queues across all faculty tests, and activate or deactivate user accounts.
          </p>
        </Card>
      </div>
    </AppLayout>
  )
}
