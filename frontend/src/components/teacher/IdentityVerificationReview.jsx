import { useEffect, useState } from 'react'
import Badge from '../shared/Badge'
import Button from '../shared/Button'
import Card from '../shared/Card'
import Modal from '../shared/Modal'
import Spinner from '../shared/Spinner'
import { useToast } from '../shared/Toast'
import { testService } from '../../services/testService'

const STATUS_VARIANTS = {
  not_submitted: 'default',
  pending: 'warning',
  verified: 'primary',
  rejected: 'danger',
}

const STATUS_LABELS = {
  not_submitted: 'Not Submitted',
  pending: 'Pending Review',
  verified: 'Verified',
  rejected: 'Rejected',
}

export default function IdentityVerificationReview({ testId, test }) {
  const [records, setRecords] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [selectedRecord, setSelectedRecord] = useState(null)
  const [reviewNotes, setReviewNotes] = useState('')
  const [reviewAction, setReviewAction] = useState(null) // 'approve' | 'reject'
  const [reviewing, setReviewing] = useState(false)
  const toast = useToast()

  useEffect(() => {
    loadRecords()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [testId])

  const loadRecords = async () => {
    setLoading(true)
    setError('')
    try {
      const data = await testService.getTestIdentityVerifications(testId)
      setRecords(data)
    } catch (err) {
      setError(err.message || 'Failed to load identity verification records')
    } finally {
      setLoading(false)
    }
  }

  const handleReview = (record, action) => {
    setSelectedRecord(record)
    setReviewAction(action)
    setReviewNotes(record.reviewer_notes || '')
  }

  const handleSubmitReview = async () => {
    if (!selectedRecord || !reviewAction) return
    setReviewing(true)
    try {
      const newStatus = reviewAction === 'approve' ? 'verified' : 'rejected'
      await testService.reviewIdentityVerification(selectedRecord.id, {
        status: newStatus,
        reviewer_notes: reviewNotes,
      })
      toast.success(
        reviewAction === 'approve'
          ? 'Identity photo verified'
          : 'Identity photo rejected'
      )
      setSelectedRecord(null)
      setReviewAction(null)
      setReviewNotes('')
      loadRecords()
    } catch (err) {
      toast.error(err.message || 'Failed to submit review')
    } finally {
      setReviewing(false)
    }
  }

  const handleCancelReview = () => {
    setSelectedRecord(null)
    setReviewAction(null)
    setReviewNotes('')
  }

  if (loading) {
    return (
      <Card>
        <div className="flex items-center gap-2">
          <Spinner size="sm" />
          <span className="text-sm text-[var(--color-text-secondary)]">
            Loading identity verifications...
          </span>
        </div>
      </Card>
    )
  }

  if (error) {
    return (
      <Card>
        <p className="text-sm text-[var(--color-danger)]">{error}</p>
      </Card>
    )
  }

  if (records.length === 0) {
    return (
      <Card>
        <h2 className="text-base font-bold mb-2 text-[var(--color-text-primary)]">
          Identity Verification
        </h2>
        <p className="text-sm text-[var(--color-text-muted)]">
          No identity verification records found for this examination.
        </p>
      </Card>
    )
  }

  return (
    <Card>
      <h2 className="text-base font-bold mb-4 text-[var(--color-text-primary)]">
        Identity Verification Review
      </h2>
      <div className="space-y-3">
        {records.map((record) => (
          <div
            key={record.id}
            className="border border-[var(--color-border)] rounded-lg p-4 space-y-2"
          >
            <div className="flex items-center justify-between gap-3">
              <div>
                <p className="font-semibold text-sm text-[var(--color-text-primary)]">
                  {record.student_name}
                </p>
                <p className="text-xs text-[var(--color-text-muted)]">
                  {record.student_email}
                </p>
              </div>
              <Badge variant={STATUS_VARIANTS[record.status] || 'default'}>
                {STATUS_LABELS[record.status] || record.status}
              </Badge>
            </div>
            <div className="flex items-center justify-between text-xs text-[var(--color-text-muted)]">
              <span>Attempt ID: {record.attempt_id}</span>
              <span>Submitted: {new Date(record.submitted_at).toLocaleString()}</span>
            </div>
            {record.status === 'pending' && (
              <div className="flex gap-2 pt-2">
                <Button
                  size="sm"
                  variant="mint"
                  onClick={() => handleReview(record, 'approve')}
                >
                  Approve
                </Button>
                <Button
                  size="sm"
                  variant="danger"
                  onClick={() => handleReview(record, 'reject')}
                >
                  Reject
                </Button>
              </div>
            )}
            {record.reviewer_notes && (
              <p className="text-xs text-[var(--color-text-secondary)] pt-2 border-t border-[var(--color-border)]">
                <span className="font-semibold">Reviewer notes:</span> {record.reviewer_notes}
              </p>
            )}
          </div>
        ))}
      </div>

      <Modal
        isOpen={!!selectedRecord && !!reviewAction}
        onClose={handleCancelReview}
        title={
          reviewAction === 'approve'
            ? 'Approve Identity Photo'
            : 'Reject Identity Photo'
        }
        footer={
          <>
            <Button variant="secondary" onClick={handleCancelReview} disabled={reviewing}>
              Cancel
            </Button>
            <Button
              variant={reviewAction === 'approve' ? 'mint' : 'danger'}
              loading={reviewing}
              onClick={handleSubmitReview}
            >
              {reviewAction === 'approve' ? 'Approve' : 'Reject'}
            </Button>
          </>
        }
      >
        <div className="space-y-4">
          <p className="text-sm text-[var(--color-text-secondary)]">
            {reviewAction === 'approve'
              ? 'Are you sure you want to approve this identity photo? The student will be marked as verified.'
              : 'Are you sure you want to reject this identity photo? The student will be able to submit a replacement photo.'}
          </p>
          <div>
            <label className="block text-xs font-semibold text-[var(--color-text-secondary)] mb-1">
              Reviewer notes (optional)
            </label>
            <textarea
              value={reviewNotes}
              onChange={(e) => setReviewNotes(e.target.value)}
              placeholder="Add notes about this review..."
              rows={3}
              className="w-full px-3 py-2 text-sm border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] resize-none"
              maxLength={2000}
            />
          </div>
        </div>
      </Modal>
    </Card>
  )
}