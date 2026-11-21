
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
  const [imageStates, setImageStates] = useState({})
  const [previewImage, setPreviewImage] = useState(null)

  const [selectedRecord, setSelectedRecord] = useState(null)
  const [reviewNotes, setReviewNotes] = useState('')
  const [reviewAction, setReviewAction] = useState(null)
  const [reviewing, setReviewing] = useState(false)

  const toast = useToast()

  useEffect(() => {
    loadRecords()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [testId])

  // Load identity photographs for every verification record.
  useEffect(() => {
    let active = true
    const objectUrls = new Set()

    setImageStates(
      Object.fromEntries(
        records.map((record) => [
          record.id,
          { status: 'loading', url: null },
        ])
      )
    )

    records.forEach(async (record) => {
      try {
        const blob = await testService.getIdentityVerificationImage(record.id)

        if (!active) return

        const url = URL.createObjectURL(blob)
        objectUrls.add(url)

        setImageStates((previous) => ({
          ...previous,
          [record.id]: {
            status: 'loaded',
            url,
          },
        }))
      } catch {
        if (!active) return

        setImageStates((previous) => ({
          ...previous,
          [record.id]: {
            status: 'error',
            url: null,
          },
        }))
      }
    })

    // Release generated image URLs when records change or component unmounts.
    return () => {
      active = false
      objectUrls.forEach((url) => URL.revokeObjectURL(url))
    }
  }, [records])

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
      const newStatus =
        reviewAction === 'approve' ? 'verified' : 'rejected'

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

      await loadRecords()
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
        {records.map((record) => {
          const image = imageStates[record.id]

          return (
            <div
              key={record.id}
              className="border border-[var(--color-border)] rounded-lg p-4 space-y-3"
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

              {/* Identity photograph */}
              <div className="rounded-lg border border-[var(--color-border)] bg-[var(--color-background)] p-3">
                <p className="text-xs font-semibold text-[var(--color-text-secondary)] mb-2">
                  Student Identity Photograph
                </p>

                {!image || image.status === 'loading' ? (
                  <div className="flex items-center gap-2 py-6 justify-center">
                    <Spinner size="sm" />
                    <span className="text-xs text-[var(--color-text-muted)]">
                      Loading photograph...
                    </span>
                  </div>
                ) : image.status === 'error' ? (
                  <p className="text-xs text-[var(--color-danger)] py-4 text-center">
                    Photograph could not be loaded.
                  </p>
                ) : (
                  <button
                    type="button"
                    onClick={() =>
                      setPreviewImage({
                        url: image.url,
                        studentName: record.student_name,
                      })
                    }
                    className="block w-full text-left cursor-zoom-in"
                    aria-label={`View identity photograph of ${record.student_name}`}
                  >
                    <img
                      src={image.url}
                      alt={`Identity verification photograph of ${record.student_name}`}
                      className="max-h-64 max-w-full mx-auto rounded-lg object-contain"
                    />
                    <p className="text-xs text-center text-[var(--color-text-muted)] mt-2">
                      Click to enlarge
                    </p>
                  </button>
                )}
              </div>

              <div className="flex items-center justify-between text-xs text-[var(--color-text-muted)]">
                <span>Attempt ID: {record.attempt_id}</span>
                <span>
                  Submitted:{' '}
                  {record.submitted_at
                    ? new Date(record.submitted_at).toLocaleString()
                    : 'N/A'}
                </span>
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
                  <span className="font-semibold">Reviewer notes:</span>{' '}
                  {record.reviewer_notes}
                </p>
              )}
            </div>
          )
        })}
      </div>

      {/* Full-size photograph preview */}
      <Modal
        isOpen={!!previewImage}
        onClose={() => setPreviewImage(null)}
        title={
          previewImage
            ? `Identity Photograph - ${previewImage.studentName}`
            : 'Identity Photograph'
        }
      >
        {previewImage && (
          <div className="flex justify-center">
            <img
              src={previewImage.url}
              alt={`Enlarged identity photograph of ${previewImage.studentName}`}
              className="max-h-[70vh] max-w-full object-contain rounded-lg"
            />
          </div>
        )}
      </Modal>

      {/* Approve / reject review modal */}
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
            <Button
              variant="secondary"
              onClick={handleCancelReview}
              disabled={reviewing}
            >
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
