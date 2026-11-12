import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import AppLayout from '../../components/layout/AppLayout'
import Button from '../../components/shared/Button'
import Card from '../../components/shared/Card'
import EmptyState from '../../components/shared/EmptyState'
import Spinner from '../../components/shared/Spinner'
import { useToast } from '../../components/shared/Toast'
import { studentService } from '../../services/studentService'
import { ROUTES } from '../../utils/constants'

export default function StudentPreExamPage() {
  const { attemptId } = useParams()
  const navigate = useNavigate()
  const toast = useToast()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleBack = () => {
    navigate(ROUTES.STUDENT_DASHBOARD)
  }

  const handleStartExamination = async () => {
    setError('')
    setLoading(true)
    try {
      const startedAttempt = await studentService.startAttempt(attemptId)
      toast.success('Examination started')
      navigate(ROUTES.STUDENT_EXAM.replace(':attemptId', String(attemptId)), {
        state: {
          timeLimitEndsAt: startedAttempt.time_limit_ends_at,
        },
      })
    } catch (err) {
      setError(err.message || 'Could not start the examination. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <AppLayout>
      <div className="space-y-8">
        <div>
          <span className="text-xs font-semibold text-[var(--color-text-muted)] uppercase tracking-wider">
            Pre-Examination
          </span>
          <h1 className="page-title mt-1">Examination Confirmed</h1>
          <p className="text-[var(--color-text-secondary)] text-sm mt-1">
            Your examination attempt has been created. Start the timed assessment when you are ready.
          </p>
        </div>

        <Card className="max-w-lg">
          <h2 className="text-base font-bold mb-4 text-[var(--color-text-primary)]">Readiness Steps</h2>
          <div className="space-y-4">
            <div className="flex items-start gap-3">
              <div className="w-6 h-6 rounded-full bg-[var(--color-surface-soft)] flex items-center justify-center text-xs font-semibold text-[var(--color-text-secondary)] shrink-0">
                1
              </div>
              <div>
                <h3 className="text-sm font-semibold text-[var(--color-text-primary)]">System Check</h3>
                <p className="text-xs text-[var(--color-text-secondary)]">
                  Verify browser compatibility and network connectivity before beginning.
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-6 h-6 rounded-full bg-[var(--color-surface-soft)] flex items-center justify-center text-xs font-semibold text-[var(--color-text-secondary)] shrink-0">
                2
              </div>
              <div>
                <h3 className="text-sm font-semibold text-[var(--color-text-primary)]">Identity Verification</h3>
                <p className="text-xs text-[var(--color-text-secondary)]">
                  Confirm your identity before accessing the examination interface.
                </p>
              </div>
            </div>
          </div>
        </Card>

        <Card
          className="max-w-lg bg-[var(--color-surface-soft)] border border-[var(--color-border)]"
        >
          <h2 className="text-base font-bold mb-2 text-[var(--color-text-primary)]">Examination Timer</h2>
          <p className="text-sm text-[var(--color-text-secondary)] mb-4">
            The examination timer <strong>has not started yet</strong>. It will begin only when you explicitly start the examination after completing the readiness steps.
          </p>
          <p className="text-xs text-[var(--color-text-muted)]">
            Attempt ID: {attemptId}
          </p>
        </Card>

        {error && (
          <Card className="max-w-lg">
            <p className="text-sm text-[var(--color-danger)]">{error}</p>
          </Card>
        )}

        <div className="flex gap-3">
          <Button
            size="lg"
            loading={loading}
            onClick={handleStartExamination}
            disabled={loading}
          >
            Start Examination →
          </Button>
          <Button variant="secondary" onClick={handleBack} size="lg">
            Back to Test Details
          </Button>
        </div>

        <EmptyState
          icon="ℹ️"
          title="Important"
          description={
            <>
              No webcam, microphone, or proctoring features are active on this page. This is a pre-examination readiness step only. The timed examination has not begun.
            </>
          }
        />
      </div>
    </AppLayout>
  )
}
