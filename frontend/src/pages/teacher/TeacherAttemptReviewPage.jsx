import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import AppLayout from '../../components/layout/AppLayout'
import Button from '../../components/shared/Button'
import Card from '../../components/shared/Card'
import Spinner from '../../components/shared/Spinner'
import EmptyState from '../../components/shared/EmptyState'
import Badge from '../../components/shared/Badge'
import { useToast } from '../../components/shared/Toast'
import { testService } from '../../services/testService'
import { ROUTES, REVIEW_STATUS_LABELS } from '../../utils/constants'

const EVENT_LABELS = {
  face_not_detected: 'Face Not Detected',
  multiple_faces_detected: 'Multiple Faces Detected',
  looking_away: 'Looking Away',
  fullscreen_exited: 'Fullscreen Exited',
  tab_visibility_changed: 'Tab Visibility Changed',
  camera_disconnected: 'Camera Disconnected',
  microphone_unavailable: 'Microphone Unavailable',
  network_interrupted: 'Network Interrupted',
  identity_check_failed: 'Identity Check Failed',
  phone_detected: 'Phone Detected',
}

const REVIEW_STATUSES = ['unreviewed', 'under_review', 'reviewed', 'no_concern', 'requires_further_review']

export default function TeacherAttemptReviewPage() {
  const { attemptId } = useParams()
  const toast = useToast()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const [events, setEvents] = useState([])
  const [eventsLoading, setEventsLoading] = useState(true)
  const [eventsError, setEventsError] = useState('')

  // per-event editing state
  const [edits, setEdits] = useState({}) // eventId -> { status, notes }
  const [saving, setSaving] = useState({}) // eventId -> bool
  const [saveErrors, setSaveErrors] = useState({}) // eventId -> string

  const load = async () => {
    setLoading(true)
    setError('')
    try {
      const res = await testService.getTeacherAttempt(attemptId)
      setData(res)
    } catch (err) {
      setError(err.message || 'Unable to load attempt details.')
    } finally {
      setLoading(false)
    }
  }

  const loadEvents = async () => {
    setEventsLoading(true)
    setEventsError('')
    try {
      const res = await testService.getProctoringEvents(attemptId)
      setEvents(Array.isArray(res) ? res : [])
    } catch (err) {
      setEventsError(err.message || 'Unable to load proctoring events.')
    } finally {
      setEventsLoading(false)
    }
  }

  useEffect(() => { load() }, [attemptId])
  useEffect(() => { loadEvents() }, [attemptId])

  const getEdit = (ev) => edits[ev.id] || { status: ev.review_status, notes: ev.reviewer_notes || '' }

  const updateEdit = (evId, field, value) => {
    setEdits((prev) => ({
      ...prev,
      [evId]: { ...getEditById(evId), [field]: value },
    }))
  }

  const getEditById = (evId) => {
    const ev = events.find((e) => e.id === evId)
    return edits[evId] || (ev ? { status: ev.review_status, notes: ev.reviewer_notes || '' } : { status: 'unreviewed', notes: '' })
  }

  const handleSave = async (ev) => {
    if (saving[ev.id]) return
    const edit = getEdit(ev)
    setSaving((prev) => ({ ...prev, [ev.id]: true }))
    setSaveErrors((prev) => ({ ...prev, [ev.id]: '' }))
    try {
      const updated = await testService.reviewProctoringEvent(attemptId, ev.id, {
        review_status: edit.status,
        reviewer_notes: edit.notes === '' ? null : edit.notes,
      })
      setEvents((prev) => prev.map((e) => (e.id === ev.id ? updated : e)))
      setEdits((prev) => {
        const next = { ...prev }
        delete next[ev.id]
        return next
      })
      toast.success('Review saved.')
    } catch (err) {
      const msg = err.message || 'Unable to save review.'
      let display = msg
      if (msg.includes('401') || msg.toLowerCase().includes('not authenticated')) display = 'Session expired. Please log in again.'
      else if (msg.includes('403') || msg.toLowerCase().includes('insufficient')) display = 'You do not have permission to review this event.'
      else if (msg.includes('404')) display = 'Event or attempt not found.'
      else if (msg.includes('422')) display = 'Invalid review data.'
      setSaveErrors((prev) => ({ ...prev, [ev.id]: display }))
    } finally {
      setSaving((prev) => ({ ...prev, [ev.id]: false }))
    }
  }

  const fmt = (v) => (v ? new Date(v).toLocaleString() : '—')

  return (
    <AppLayout>
      <div className="space-y-6">
        <div>
          <Link to={data ? ROUTES.TEACHER_ATTEMPTS.replace(':testId', data.test_id) : ROUTES.TEACHER_TESTS} className="text-xs font-semibold text-[var(--color-text-secondary)]">
            ← Back to Attempts
          </Link>
          <h1 className="page-title mt-2">Attempt Review</h1>
        </div>

        {loading && <Spinner />}
        {error && <Card><p className="text-sm text-red-600">{error}</p></Card>}

        {!loading && !error && data && (
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <h2 className="text-sm font-semibold mb-2">Student</h2>
              <p className="text-sm">{data.student_name}</p>
              <p className="text-xs text-[var(--color-text-muted)]">{data.student_email}</p>
              <p className="text-xs text-[var(--color-text-muted)]">ID: {data.student_id}</p>
            </Card>
            <Card>
              <h2 className="text-sm font-semibold mb-2">Examination</h2>
              <p className="text-sm">{data.test_title}</p>
              <p className="text-xs text-[var(--color-text-muted)]">Test ID: {data.test_id}</p>
            </Card>
            <Card>
              <h2 className="text-sm font-semibold mb-2">Attempt</h2>
              <p className="text-xs">Attempt ID: {data.attempt_id}</p>
              <p className="text-xs">Status: {data.status}</p>
              <p className="text-xs">Warnings: {data.warning_count}</p>
              <p className="text-xs">Proctoring events: {data.proctoring_event_count}</p>
              <p className="text-xs">Identity verified: {data.identity_verified ? 'Yes' : 'No'}</p>
              {data.identity_verification_status && (
                <p className="text-xs">Identity status: {data.identity_verification_status}</p>
              )}
              <p className="text-xs">Started: {fmt(data.started_at)}</p>
              <p className="text-xs">Submitted: {fmt(data.submitted_at)}</p>
            </Card>
          </div>
        )}

        <Card>
          <h2 className="text-sm font-semibold mb-3">Proctoring Events</h2>
          {eventsLoading && <Spinner />}
          {eventsError && (
            <div className="space-y-2">
              <p className="text-sm text-red-600">{eventsError}</p>
              <Button variant="secondary" size="sm" onClick={loadEvents}>Retry</Button>
            </div>
          )}
          {!eventsLoading && !eventsError && events.length === 0 && (
            <EmptyState title="No proctoring events" description="No proctoring events recorded for this attempt." />
          )}
          {!eventsLoading && !eventsError && events.length > 0 && (
            <ol className="relative border-l border-[var(--color-border)] ml-2 space-y-6">
              {events.map((ev) => {
                const edit = getEdit(ev)
                return (
                  <li key={ev.id} className="ml-4 space-y-2">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="text-sm font-medium">{EVENT_LABELS[ev.event_type] || ev.event_type}</span>
                      <Badge variant={ev.severity === 'high' ? 'danger' : ev.severity === 'medium' ? 'warning' : 'neutral'}>{ev.severity}</Badge>
                      <span className="text-xs text-[var(--color-text-muted)]">{new Date(ev.timestamp).toLocaleString()}</span>
                    </div>
                    {ev.description && (
                      <p className="text-xs text-[var(--color-text-secondary)]">{ev.description}</p>
                    )}
                    {ev.duration_seconds != null && (
                      <p className="text-xs text-[var(--color-text-muted)]">Duration: {ev.duration_seconds}s</p>
                    )}
                    <p className="text-xs text-[var(--color-text-muted)]">Reviewer: {ev.reviewer_id ?? '—'} · {ev.reviewed_at ? new Date(ev.reviewed_at).toLocaleString() : 'not reviewed'}</p>

                    <div className="space-y-2 pt-2">
                      <select
                        className="text-xs border border-[var(--color-border)] rounded px-2 py-1"
                        value={edit.status}
                        onChange={(e) => updateEdit(ev.id, 'status', e.target.value)}
                        disabled={saving[ev.id]}
                      >
                        {REVIEW_STATUSES.map((s) => (
                          <option key={s} value={s}>{REVIEW_STATUS_LABELS[s] || s}</option>
                        ))}
                      </select>
                      <textarea
                        className="w-full text-xs border border-[var(--color-border)] rounded p-2"
                        rows={2}
                        maxLength={2000}
                        placeholder="Reviewer notes (max 2000 chars)"
                        value={edit.notes}
                        onChange={(e) => updateEdit(ev.id, 'notes', e.target.value)}
                        disabled={saving[ev.id]}
                      />
                      {saveErrors[ev.id] && (
                        <p className="text-xs text-red-600">{saveErrors[ev.id]}</p>
                      )}
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => handleSave(ev)}
                        disabled={saving[ev.id]}
                      >
                        {saving[ev.id] ? 'Saving…' : 'Save Review'}
                      </Button>
                    </div>
                  </li>
                )
              })}
            </ol>
          )}
        </Card>

        <div>
          <Button variant="secondary" onClick={load}>Refresh</Button>
        </div>
      </div>
    </AppLayout>
  )
}
