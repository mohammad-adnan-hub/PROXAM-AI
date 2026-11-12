import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import AppLayout from '../../components/layout/AppLayout'
import Badge from '../../components/shared/Badge'
import Button from '../../components/shared/Button'
import Card from '../../components/shared/Card'
import Modal from '../../components/shared/Modal'
import Spinner from '../../components/shared/Spinner'
import { useToast } from '../../components/shared/Toast'
import { testService } from '../../services/testService'
import { ROUTES } from '../../utils/constants'
import { copyToClipboard, formatDateTime, formatDuration } from '../../utils/formatters'

export default function TeacherTestDetailsPage() {
  const { testId } = useParams()
  const navigate = useNavigate()
  const toast = useToast()
  const [test, setTest] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [confirmDelete, setConfirmDelete] = useState(false)
  const [deleting, setDeleting] = useState(false)

  useEffect(() => {
    const load = async () => {
      setLoading(true)
      setError('')
      try {
        const data = await testService.getTestDetails(testId)
        setTest(data)
      } catch (err) {
        setError(err.message || 'Examination not found.')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [testId])

  const handleCopy = async () => {
    try {
      await copyToClipboard(test.test_code)
      toast.success('Examination code copied')
    } catch {
      toast.error('Could not copy code')
    }
  }

  const handleDelete = async () => {
    setDeleting(true)
    try {
      await testService.deleteTest(testId)
      toast.success('Examination deleted')
      navigate(ROUTES.TEACHER_DASHBOARD)
    } catch (err) {
      toast.error(err.message || 'Could not delete examination')
    } finally {
      setDeleting(false)
      setConfirmDelete(false)
    }
  }

  return (
    <AppLayout>
      {loading && (
        <div className="flex justify-center py-16">
          <Spinner size="lg" />
        </div>
      )}

      {!loading && error && (
        <Card>
          <p className="text-sm mb-4">{error}</p>
          <Link to={ROUTES.TEACHER_TESTS}>
            <Button variant="secondary" size="sm">
              Back to My Tests
            </Button>
          </Link>
        </Card>
      )}

      {!loading && test && (
        <div className="space-y-6">
          <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
            <div>
              <Link to={ROUTES.TEACHER_TESTS} className="text-xs font-semibold text-[var(--color-text-secondary)]">
                ← Back to My Tests
              </Link>
              <h1 className="page-title mt-2">{test.title}</h1>
              <div className="flex flex-wrap items-center gap-2 mt-2">
                <Badge variant="success">{test.status}</Badge>
                <span className="font-mono text-sm font-semibold">{test.test_code}</span>
              </div>
            </div>
            <div className="flex gap-2">
              <Button variant="secondary" onClick={handleCopy}>
                Copy code
              </Button>
              {test.attempt_count === 0 && (
                <Button variant="danger" onClick={() => setConfirmDelete(true)}>
                  Delete
                </Button>
              )}
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card>
              <p className="text-xs uppercase text-[var(--color-text-muted)]">Duration</p>
              <p className="font-semibold mt-1">{formatDuration(test.duration_minutes)}</p>
            </Card>
            <Card>
              <p className="text-xs uppercase text-[var(--color-text-muted)]">Questions</p>
              <p className="font-semibold mt-1">{test.question_count}</p>
            </Card>
            <Card>
              <p className="text-xs uppercase text-[var(--color-text-muted)]">Total marks</p>
              <p className="font-semibold mt-1">{test.total_marks}</p>
            </Card>
            <Card>
              <p className="text-xs uppercase text-[var(--color-text-muted)]">Attempts</p>
              <p className="font-semibold mt-1">{test.attempt_count}</p>
            </Card>
          </div>

          {test.description && (
            <Card>
              <h2 className="text-sm font-bold mb-2">Description</h2>
              <p className="text-sm text-[var(--color-text-secondary)] whitespace-pre-wrap">{test.description}</p>
            </Card>
          )}

          {test.instructions && (
            <Card>
              <h2 className="text-sm font-bold mb-2">Instructions</h2>
              <p className="text-sm text-[var(--color-text-secondary)] whitespace-pre-wrap">{test.instructions}</p>
            </Card>
          )}

          <p className="text-xs text-[var(--color-text-muted)]">
            Created {formatDateTime(test.created_at)}
          </p>

          <div className="space-y-4">
            <h2 className="text-base font-bold">Questions</h2>
            {test.questions?.map((question, index) => (
              <Card key={question.id}>
                <div className="flex justify-between gap-4 mb-3">
                  <h3 className="font-semibold text-sm">
                    {index + 1}. {question.question_text}
                  </h3>
                  <span className="text-xs text-[var(--color-text-muted)] shrink-0">
                    {question.marks} mark{question.marks === 1 ? '' : 's'}
                  </span>
                </div>
                <ul className="space-y-2">
                  {question.options.map((opt) => (
                    <li
                      key={opt.id}
                      className={[
                        'text-sm px-3 py-2 rounded-md border',
                        opt.is_correct
                          ? 'border-[var(--color-mint-strong)] bg-[var(--color-mint)]/40'
                          : 'border-[var(--color-border)]',
                      ].join(' ')}
                    >
                      <span className="font-semibold mr-2">{opt.label}.</span>
                      {opt.option_text}
                      {opt.is_correct && (
                        <span className="ml-2 text-[11px] font-semibold uppercase">Correct</span>
                      )}
                    </li>
                  ))}
                </ul>
              </Card>
            ))}
          </div>
        </div>
      )}

      <Modal
        isOpen={confirmDelete}
        onClose={() => setConfirmDelete(false)}
        title="Delete examination"
        footer={
          <>
            <Button variant="secondary" onClick={() => setConfirmDelete(false)}>
              Cancel
            </Button>
            <Button variant="danger" loading={deleting} onClick={handleDelete}>
              Delete
            </Button>
          </>
        }
      >
        <p className="text-sm text-[var(--color-text-secondary)]">
          This will permanently remove the examination and its questions. This cannot be undone.
        </p>
      </Modal>
    </AppLayout>
  )
}
