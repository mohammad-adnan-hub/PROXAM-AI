import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import AppLayout from '../../components/layout/AppLayout'
import Badge from '../../components/shared/Badge'
import Button from '../../components/shared/Button'
import Card from '../../components/shared/Card'
import EmptyState from '../../components/shared/EmptyState'
import Spinner from '../../components/shared/Spinner'
import { useToast } from '../../components/shared/Toast'
import { studentService } from '../../services/studentService'
import { ROUTES } from '../../utils/constants'
import { formatDuration } from '../../utils/formatters'

export default function StudentTestDetailsPage() {
  const { testId } = useParams()
  const navigate = useNavigate()
  const toast = useToast()
  const [test, setTest] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [creating, setCreating] = useState(false)
  const [createError, setCreateError] = useState('')

  useEffect(() => {
    const load = async () => {
      setLoading(true)
      setError('')
      try {
        const data = await studentService.getStudentTestDetails(testId)
        setTest(data)
      } catch (err) {
        setError(err.message || 'Examination not found or not accessible.')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [testId])

  const handleBack = () => {
    navigate(ROUTES.STUDENT_DASHBOARD)
  }

  const handleCreateAttempt = async () => {
    setCreateError('')
    setCreating(true)
    try {
      const attempt = await studentService.createAttempt(testId)
      toast.success('Examination attempt created')
      navigate(ROUTES.STUDENT_SYSTEM_CHECK.replace(':attemptId', String(attempt.id)))
    } catch (err) {
      setCreateError(err.message || 'Could not create examination attempt. Please try again.')
    } finally {
      setCreating(false)
    }
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
          <Button variant="secondary" onClick={handleBack} fullWidth>
            Return to Dashboard
          </Button>
        </Card>
      </AppLayout>
    )
  }

  if (!test) {
    return (
      <AppLayout>
        <EmptyState
          icon="🔍"
          title="Examination not found"
          description="The examination you are looking for could not be found or is no longer active."
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
            <h1 className="page-title mt-2">{test.title}</h1>
            <div className="flex flex-wrap items-center gap-2 mt-2">
              <Badge variant="success">{test.status}</Badge>
              <span className="font-mono text-sm font-semibold">{test.test_code}</span>
            </div>
          </div>
          <Button variant="secondary" onClick={handleBack} size="sm">
            Back
          </Button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <p className="text-xs uppercase text-[var(--color-text-muted)]">Duration</p>
            <p className="font-semibold mt-1">{formatDuration(test.duration_minutes)}</p>
          </Card>
          <Card>
            <p className="text-xs uppercase text-[var(--color-text-muted)]">Total questions</p>
            <p className="font-semibold mt-1">{test.question_count}</p>
          </Card>
          <Card>
            <p className="text-xs uppercase text-[var(--color-text-muted)]">Total marks</p>
            <p className="font-semibold mt-1">{test.total_marks}</p>
          </Card>
          <Card>
            <p className="text-xs uppercase text-[var(--color-text-muted)]">Status</p>
            <p className="font-semibold mt-1">{test.status}</p>
          </Card>
        </div>

        {test.description && (
          <Card>
            <h2 className="text-sm font-bold mb-2">Description</h2>
            <p className="text-sm text-[var(--color-text-secondary)] whitespace-pre-wrap">{test.description}</p>
          </Card>
        )}

        <div className="bg-[var(--color-surface-soft)] border border-[var(--color-border)] rounded-xl p-6">
          <h2 className="text-base font-bold mb-4 text-[var(--color-text-primary)]">Next Steps</h2>
          <p className="text-sm text-[var(--color-text-secondary)] mb-4">
            Your examination details have been confirmed. Proceed to system check and identity verification before starting the timed assessment.
          </p>
          {createError && (
            <p className="text-xs text-[var(--color-danger)] mb-4">{createError}</p>
          )}
        </div>

        <Button
          size="lg"
          fullWidth
          loading={creating}
          disabled={creating}
          onClick={handleCreateAttempt}
        >
          Continue to Examination →
        </Button>

        <p className="text-xs text-[var(--color-text-muted)]">
          Code: {test.test_code}
        </p>
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
