import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import AppLayout from '../../components/layout/AppLayout'
import Button from '../../components/shared/Button'
import Card from '../../components/shared/Card'
import Spinner from '../../components/shared/Spinner'
import { useToast } from '../../components/shared/Toast'
import { testService } from '../../services/testService'
import { ROUTES } from '../../utils/constants'

export default function TeacherAttemptsPage() {
  const { testId } = useParams()
  const toast = useToast()
  const [attempts, setAttempts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const load = async () => {
    setLoading(true)
    setError('')
    try {
      const data = await testService.getTestAttempts(testId)
      setAttempts(data)
    } catch (err) {
      const msg = err.message || 'Unable to load attempts.'
      if (msg.includes('401') || msg.toLowerCase().includes('not authenticated')) {
        setError('You are not signed in. Please log in again.')
      } else if (msg.includes('403') || msg.toLowerCase().includes('insufficient')) {
        setError('You do not have permission to view these attempts.')
      } else {
        setError(msg)
      }
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [testId])

  return (
    <AppLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="page-title">Proctoring Review — Attempts</h1>
          <Button variant="secondary" onClick={load}>Refresh</Button>
        </div>
        {loading && <Spinner />}
        {error && <p className="text-sm text-red-600">{error}</p>}
        {!loading && !error && attempts.length === 0 && (
          <Card><p className="text-sm text-[var(--color-text-muted)]">No attempts found.</p></Card>
        )}
        {!loading && attempts.length > 0 && (
          <div className="space-y-3">
            {attempts.map((a) => (
              <Card key={a.attempt_id}>
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
                <div>
                    <p className="font-medium">{a.student_name}</p>
                    <p className="text-xs text-[var(--color-text-muted)]">{a.student_email}</p>
                    <p className="text-xs">Status: {a.status} · Warnings: {a.warning_count} · Identity: {a.identity_verified ? 'Verified' : 'Not verified'} · Events: {a.proctoring_event_count}</p>
                    <p className="text-xs text-[var(--color-text-muted)]">Started: {a.started_at ? new Date(a.started_at).toLocaleString() : '—'} · Submitted: {a.submitted_at ? new Date(a.submitted_at).toLocaleString() : '—'}</p>
                    {a.latest_event_type && (
                      <p className="text-xs text-[var(--color-text-muted)]">Latest: {a.latest_event_type} ({a.latest_event_severity}) {a.latest_event_timestamp ? new Date(a.latest_event_timestamp).toLocaleString() : ''}</p>
                    )}
                    {a.warning_count >= 4 && (
                      <p className="text-xs text-red-600">Terminated after 4 qualifying warnings.</p>
                    )}
                  </div>
                  <Link to={ROUTES.TEACHER_REVIEW.replace(':attemptId', a.attempt_id)} className="text-sm text-[var(--color-primary)]">Review</Link>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </AppLayout>
  )
}
