import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import AppLayout from '../../components/layout/AppLayout'
import Badge from '../../components/shared/Badge'
import Button from '../../components/shared/Button'
import Card from '../../components/shared/Card'
import EmptyState from '../../components/shared/EmptyState'
import Spinner from '../../components/shared/Spinner'
import { useToast } from '../../components/shared/Toast'
import { studentService } from '../../services/studentService'
import { ROUTES } from '../../utils/constants'
import { formatDate, formatPercentage } from '../../utils/formatters'

const statusVariant = {
  created: 'warning',
  in_progress: 'warning',
  submitted: 'success',
  timed_out: 'danger',
}

export default function StudentHistory() {
  const navigate = useNavigate()
  const toast = useToast()
  const [attempts, setAttempts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const load = async () => {
      setLoading(true)
      setError('')
      try {
        const data = await studentService.getStudentAttempts()
        setAttempts(data || [])
      } catch (err) {
        setError(err.message || 'Could not load your examination records. Please try again.')
        setAttempts([])
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  const handleBack = () => {
    navigate(ROUTES.STUDENT_DASHBOARD)
  }

  const handleRetry = () => {
    setError('')
    setLoading(true)
    studentService.getStudentAttempts()
      .then((data) => setAttempts(data || []))
      .catch((err) => {
        setError(err.message || 'Could not load your examination records. Please try again.')
        setAttempts([])
      })
      .finally(() => setLoading(false))
  }

  const handleViewResult = (attemptId) => {
    navigate(ROUTES.STUDENT_EXAM.replace(':attemptId', String(attemptId)))
  }

  if (loading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center min-h-screen bg-[var(--color-background)]">
          <Spinner size="lg" />
        </div>
      </AppLayout>
    )
  }

  if (!loading && error) {
    return (
      <AppLayout>
        <Card className="max-w-md mx-auto">
          <p className="text-sm mb-6">{error}</p>
          <div className="flex items-center gap-2">
            <Button variant="secondary" onClick={handleRetry} size="sm">
              Retry
            </Button>
            <Button variant="secondary" onClick={handleBack} size="sm">
              Return to Dashboard
            </Button>
          </div>
        </Card>
      </AppLayout>
    )
  }

  if (!attempts || attempts.length === 0) {
    return (
      <AppLayout>
        <EmptyState
          icon="📝"
          title="No Examination Records Yet"
          description="You have not attempted any examinations. When you complete an assessment, your verified submission and grade summary will appear here."
          action={
            <Button variant="secondary" size="sm" onClick={handleBack}>
              Return to Dashboard
            </Button>
          }
        />
      </AppLayout>
    )
  }

  return (
    <AppLayout>
      <div className="space-y-6">
        <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
          <div>
            <LinkBack onClick={handleBack}>
              ← Return to Dashboard
            </LinkBack>
            <h1 className="page-title mt-2">My Records</h1>
            <p className="text-xs text-[var(--color-text-muted)]">
              Your examination history, scores and results.
            </p>
          </div>
          <Button variant="secondary" onClick={handleBack} size="sm">
            Back
          </Button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead>
              <tr className="text-[11px] uppercase tracking-wider text-[var(--color-text-muted)] border-b border-[var(--color-border)]">
                <th className="py-3 pr-4 font-semibold">Examination</th>
                <th className="py-3 pr-4 font-mono text-xs">Code</th>
                <th className="py-3 pr-4 font-semibold">Date</th>
                <th className="py-3 pr-4 font-semibold">Status</th>
                <th className="py-3 pr-4 font-semibold">Score</th>
                <th className="py-3 pr-4 font-semibold">Percentage</th>
                <th className="py-3 font-semibold">Result</th>
              </tr>
            </thead>
            <tbody>
              {attempts.map((attempt) => {
                const isFinalized =
                  attempt.status === 'submitted' || attempt.status === 'timed_out'
                const hasResult =
                  isFinalized && attempt.score !== null && attempt.percentage !== null
                return (
                  <tr
                    key={attempt.id}
                    className="border-b border-[var(--color-border)] last:border-0 hover:bg-[var(--color-surface-soft)]"
                  >
                    <td className="py-3 pr-4 font-medium">
                      {attempt.test_title || 'Untitled Examination'}
                    </td>
                    <td className="py-3 pr-4 font-mono text-xs">
                      {attempt.test_code || '—'}
                    </td>
                    <td className="py-3 pr-4">
                      {formatDate(attempt.created_at)}
                    </td>
                    <td className="py-3 pr-4">
                      <Badge variant={statusVariant[attempt.status] || 'default'}>
                        {attempt.status.replace('_', ' ')}
                      </Badge>
                    </td>
                    <td className="py-3 pr-4">
                      {hasResult ? (
                        <span className="font-semibold">{attempt.score} / {attempt.total_marks}</span>
                      ) : (
                        <span className="text-[var(--color-text-muted)]">—</span>
                      )}
                    </td>
                    <td className="py-3 pr-4">
                      {hasResult ? (
                        <span className="font-semibold">{formatPercentage(attempt.percentage)}</span>
                      ) : (
                        <span className="text-[var(--color-text-muted)]">—</span>
                      )}
                    </td>
                    <td className="py-3">
                      {isFinalized ? (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleViewResult(attempt.id)}
                        >
                          View Result
                        </Button>
                      ) : attempt.status === 'in_progress' ? (
                        <span className="text-xs text-[var(--color-text-muted)]">In progress</span>
                      ) : (
                        <span className="text-xs text-[var(--color-text-muted)]">Not started</span>
                      )}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>

        {attempts.some(
          (a) => a.status === 'submitted' || a.status === 'timed_out',
        ) && (
          <p className="text-xs text-[var(--color-text-muted)] mt-4">
            Click <strong>View Result</strong> on a finalized attempt to see your full result breakdown.
          </p>
        )}
      </div>
    </AppLayout>
  )
}

function LinkBack({ onClick, children }) {
  return (
    <a
      onClick={(e) => {
        e.preventDefault()
        onClick()
      }}
      className="text-xs font-semibold text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]"
    >
      {children}
    </a>
  )
}
