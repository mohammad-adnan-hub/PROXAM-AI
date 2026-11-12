import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import AppLayout from '../../components/layout/AppLayout'
import Button from '../../components/shared/Button'
import Card from '../../components/shared/Card'
import Spinner from '../../components/shared/Spinner'
import TestListTable from '../../components/teacher/TestListTable'
import { useAuth } from '../../context/AuthContext'
import { useToast } from '../../components/shared/Toast'
import { testService } from '../../services/testService'
import { ROUTES } from '../../utils/constants'

export default function TeacherDashboard() {
  const { user } = useAuth()
  const toast = useToast()
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const loadStats = async () => {
    setLoading(true)
    setError('')
    try {
      const data = await testService.getTeacherStats()
      setStats(data)
    } catch (err) {
      setError(err.message || 'Unable to load dashboard data.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadStats()
  }, [])

  return (
    <AppLayout>
      <div className="space-y-8">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <span className="text-xs font-semibold text-[var(--color-text-muted)] uppercase tracking-wider">
              Faculty Studio
            </span>
            <h1 className="page-title mt-1">Manage your examinations</h1>
            <p className="text-[var(--color-text-secondary)] text-sm mt-1">
              Welcome back, {user?.full_name}. Author assessments, distribute generated codes, and review your records.
            </p>
          </div>
          <Link to={ROUTES.TEACHER_CREATE_DETAILS}>
            <Button size="lg">+ Create New Test</Button>
          </Link>
        </div>

        {loading && (
          <div className="flex justify-center py-16">
            <Spinner size="lg" />
          </div>
        )}

        {!loading && error && (
          <Card>
            <p className="text-sm text-[var(--color-text-primary)] mb-3">{error}</p>
            <Button size="sm" variant="secondary" onClick={loadStats}>
              Retry
            </Button>
          </Card>
        )}

        {!loading && !error && stats && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <Card accent="mint">
                <span className="text-xs font-semibold text-[var(--color-text-secondary)] uppercase">
                  Tests Created
                </span>
                <p className="text-3xl font-display font-extrabold mt-2">{stats.total_tests}</p>
                <p className="text-xs text-[var(--color-text-secondary)] mt-1">
                  {stats.active_tests} active assessment{stats.active_tests === 1 ? '' : 's'}
                </p>
              </Card>
              <Card accent="lavender">
                <span className="text-xs font-semibold text-[var(--color-text-secondary)] uppercase">
                  Total Submissions
                </span>
                <p className="text-3xl font-display font-extrabold mt-2">{stats.total_attempts}</p>
                <p className="text-xs text-[var(--color-text-secondary)] mt-1">Candidate attempts recorded</p>
              </Card>
              <Card accent="peach">
                <span className="text-xs font-semibold text-[var(--color-text-secondary)] uppercase">
                  Active Examinations
                </span>
                <p className="text-3xl font-display font-extrabold mt-2">{stats.active_tests}</p>
                <p className="text-xs text-[var(--color-text-secondary)] mt-1">Ready for student access</p>
              </Card>
            </div>

            <div>
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-base font-bold text-[var(--color-text-primary)]">Recent examinations</h2>
                <Link to={ROUTES.TEACHER_TESTS} className="text-xs font-semibold underline">
                  View all
                </Link>
              </div>
              <Card className={stats.recent_tests?.length ? 'p-0 overflow-hidden' : ''}>
                <div className={stats.recent_tests?.length ? 'p-6' : ''}>
                  <TestListTable
                    tests={stats.recent_tests}
                    onCopied={(code) =>
                      code ? toast.success(`Copied ${code}`) : toast.error('Could not copy code')
                    }
                  />
                </div>
              </Card>
            </div>
          </>
        )}
      </div>
    </AppLayout>
  )
}
