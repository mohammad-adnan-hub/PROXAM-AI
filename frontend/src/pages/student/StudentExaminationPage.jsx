import { useCallback, useEffect, useRef, useState } from 'react'
import { useLocation, useNavigate, useParams } from 'react-router-dom'
import AppLayout from '../../components/layout/AppLayout'
import Badge from '../../components/shared/Badge'
import Button from '../../components/shared/Button'
import Card from '../../components/shared/Card'
import EmptyState from '../../components/shared/EmptyState'
import Modal from '../../components/shared/Modal'
import Spinner from '../../components/shared/Spinner'
import { useToast } from '../../components/shared/Toast'
import { studentService } from '../../services/studentService'
import { ROUTES } from '../../utils/constants'
import { formatCountdown } from '../../utils/formatters'

export default function StudentExaminationPage() {
  const { attemptId } = useParams()
  const location = useLocation()
  const navigate = useNavigate()
  const toast = useToast()
  const [questions, setQuestions] = useState([])
  const [answers, setAnswers] = useState({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [pendingSaves, setPendingSaves] = useState(new Set())
  const [saveErrors, setSaveErrors] = useState({})
  const [submissionState, setSubmissionState] = useState('idle')
  const [confirmOpen, setConfirmOpen] = useState(false)
  const [pendingWriteConfirmOpen, setPendingWriteConfirmOpen] = useState(false)
  const [pendingWriteMessage, setPendingWriteMessage] = useState(
    'Some answer saves are still pending. If you submit now, those answers might not be recorded.',
  )
  const [finalStatus, setFinalStatus] = useState(null)
  const [finalResult, setFinalResult] = useState(null)
  const [remainingSeconds, setRemainingSeconds] = useState(null)
  const [deadline, setDeadline] = useState(null)

  // Ref to latest answers state (avoids stale closures in rapid interactions)
  const answersRef = useRef(answers)
  answersRef.current = answers

  // Per-question write queue: one write at a time per question
  const writeQueueRef = useRef({})
  const submissionRef = useRef(false)
  const timerRef = useRef(null)
  const deadlineRef = useRef(null)

  const getQueue = (questionId) => {
    if (!writeQueueRef.current[questionId]) {
      writeQueueRef.current[questionId] = {
        inFlight: false,
        queued: null,
      }
    }
    return writeQueueRef.current[questionId]
  }

  const sendWrite = async (questionId, payload) => {
    const queue = getQueue(questionId)
    queue.inFlight = true

    setPendingSaves((prev) => new Set([...prev, questionId]))
    setSaveErrors((prev) => {
      const next = { ...prev }
      delete next[questionId]
      return next
    })

    try {
      if (payload.type === 'put') {
        await studentService.saveAnswer(
          attemptId,
          questionId,
          payload.selectedOptionId,
          payload.isMarkedForReview,
        )
      } else {
        await studentService.clearAnswer(attemptId, questionId)
      }

      queue.inFlight = false
      const queued = queue.queued
      queue.queued = null

      setPendingSaves((prev) => {
        const next = new Set(prev)
        next.delete(questionId)
        return next
      })

      if (queued) {
        sendWrite(questionId, queued)
      }
    } catch (err) {
      queue.inFlight = false

      setPendingSaves((prev) => {
        const next = new Set(prev)
        next.delete(questionId)
        return next
      })

      const queued = queue.queued
      queue.queued = null

      if (queued) {
        setSaveErrors((prev) => ({
          ...prev,
          [questionId]: err.message || 'Failed to save answer.',
        }))
        toast.error(`Could not save answer for question ${questionId}.`)
        sendWrite(questionId, queued)
      } else {
        setSaveErrors((prev) => ({
          ...prev,
          [questionId]: err.message || 'Failed to save answer.',
        }))
        toast.error(`Could not save answer for question ${questionId}.`)
      }
    }
  }

  const enqueueWrite = (questionId, payload) => {
    if (submissionRef.current) {
      return
    }
    const queue = getQueue(questionId)

    if (queue.inFlight) {
      queue.queued = payload
      return
    }

    sendWrite(questionId, payload)
  }

  const waitForPendingWrites = useCallback(() => {
    return new Promise((resolve) => {
      let timeoutId = null
      const startTimeout = () => {
        timeoutId = setTimeout(() => {
          resolve({ timedOut: true })
        }, 10000)
      }
      startTimeout()

      const check = () => {
        if (pendingSaves.size === 0) {
          clearTimeout(timeoutId)
          resolve({ timedOut: false })
        } else {
          setTimeout(check, 50)
        }
      }
      check()
    })
  }, [pendingSaves])

  const recoverDeadline = useCallback(async () => {
    const navState = location.state
    const navDeadline = navState?.timeLimitEndsAt

    if (navDeadline) {
      const deadlineMs = new Date(navDeadline).getTime()
      deadlineRef.current = deadlineMs
      setDeadline(deadlineMs)
      return
    }

    try {
      const startedAttempt = await studentService.startAttempt(attemptId)
      const deadlineMs = new Date(
        startedAttempt.time_limit_ends_at,
      ).getTime()
      deadlineRef.current = deadlineMs
      setDeadline(deadlineMs)
    } catch (err) {
      throw new Error(
        err.message || 'Could not recover examination deadline.',
      )
    }
  }, [attemptId, location.state])

  const handleFinalizedSubmit = async () => {
    submissionRef.current = true
    try {
      const response = await studentService.submitAttempt(attemptId)
      setSubmissionState(response.status || 'submitted')
      setFinalStatus(response.status || 'submitted')
      setFinalResult(response.result || null)
      submissionRef.current = false
      toast.success(
        response.status === 'timed_out'
          ? 'Time expired. Your examination has ended.'
          : 'Examination submitted successfully.',
      )
    } catch (err) {
      submissionRef.current = false
      toast.error(err.message || 'Could not load examination details.')
    }
  }

  useEffect(() => {
    const load = async () => {
      setLoading(true)
      setError('')
      try {
        // Step 1: Check if the attempt is already finalized by fetching its result.
        // The result endpoint returns 200 only for submitted/timed_out attempts
        // that have a result record. If it returns 409 "Attempt has not been
        // finalized", we continue with the normal in-progress flow.
        let resultData = null
        try {
          resultData = await studentService.getAttemptResult(attemptId)
        } catch (resultErr) {
          const detail = resultErr.message || ''
          const isNotFinalized = detail.includes('has not been finalized')
          const isNoResult = detail.includes('Result not yet available')

          if (isNotFinalized) {
            // Attempt is still in progress - continue to normal recovery flow
            resultData = null
          } else if (isNoResult) {
            // Attempt is finalized but result not yet available.
            // submitAttempt is idempotent and returns the existing status.
            await handleFinalizedSubmit()
            setLoading(false)
            return
          } else {
            throw resultErr
          }
        }

        if (resultData) {
          // Attempt is finalized with a result. Restore result UI directly
          // from the GET result response without calling submitAttempt again.
          setSubmissionState(resultData.status || 'submitted')
          setFinalStatus(resultData.status || 'submitted')
          setFinalResult(resultData)
          setLoading(false)
          return
        }

        // Step 2: Normal in-progress recovery flow.
        await recoverDeadline()

        const [questionsData, answersData] = await Promise.all([
          studentService.getAttemptQuestions(attemptId),
          studentService.getSavedAnswers(attemptId),
        ])

        setQuestions(questionsData || [])

        const reconstructed = {}
        ;(answersData || []).forEach((answer) => {
          reconstructed[answer.question_id] = {
            selectedOptionId: answer.selected_option_id,
            isMarkedForReview: answer.is_marked_for_review,
          }
        })
        setAnswers(reconstructed)
        answersRef.current = reconstructed
      } catch (err) {
        setError(err.message || 'Could not load examination. Please try again.')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [attemptId, recoverDeadline])

  useEffect(() => {
    if (!deadline) return

    const initialRemaining = deadlineRef.current - Date.now()
    setRemainingSeconds(Math.max(0, Math.ceil(initialRemaining / 1000)))

    const tick = () => {
      const remaining = deadlineRef.current - Date.now()
      setRemainingSeconds(Math.max(0, Math.ceil(remaining / 1000)))
      if (remaining <= 0) {
        if (timerRef.current) {
          clearInterval(timerRef.current)
          timerRef.current = null
        }
        handleAutoSubmit()
      }
    }

    tick()
    timerRef.current = setInterval(tick, 1000)

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current)
        timerRef.current = null
      }
    }
  }, [deadline])

  const handleBack = () => {
    navigate(ROUTES.STUDENT_DASHBOARD)
  }

  const isSelected = (questionId, optionId) => {
    return answers[questionId]?.selectedOptionId === optionId
  }

  const isMarkedForReview = (questionId) => {
    return answers[questionId]?.isMarkedForReview === true
  }

  const isSaving = (questionId) => {
    return pendingSaves.has(questionId)
  }

  const isFinalized = () => {
    return submissionState === 'submitted' || submissionState === 'timed_out'
  }

  const handleSelectOption = (questionId, optionId) => {
    if (isFinalized()) return
    if (submissionRef.current) return
    const current = answersRef.current[questionId] || {}
    const nextState = {
      ...current,
      selectedOptionId: optionId,
    }

    answersRef.current = { ...answersRef.current, [questionId]: nextState }
    setAnswers((prev) => ({
      ...prev,
      [questionId]: nextState,
    }))

    enqueueWrite(questionId, {
      type: 'put',
      selectedOptionId: optionId,
      isMarkedForReview: current.isMarkedForReview ?? false,
    })
  }

  const handleToggleReview = (questionId) => {
    if (isFinalized()) return
    if (submissionRef.current) return
    const current = answersRef.current[questionId] || {}
    const nextReview = !current.isMarkedForReview
    const nextState = {
      ...current,
      isMarkedForReview: nextReview,
    }

    answersRef.current = { ...answersRef.current, [questionId]: nextState }
    setAnswers((prev) => ({
      ...prev,
      [questionId]: nextState,
    }))

    enqueueWrite(questionId, {
      type: 'put',
      selectedOptionId: current.selectedOptionId ?? null,
      isMarkedForReview: nextReview,
    })
  }

  const handleClearAnswer = (questionId) => {
    if (isFinalized()) return
    if (submissionRef.current) return
    const current = answersRef.current[questionId] || {}
    const nextState = {
      ...current,
      selectedOptionId: null,
    }

    answersRef.current = { ...answersRef.current, [questionId]: nextState }
    setAnswers((prev) => ({
      ...prev,
      [questionId]: nextState,
    }))

    enqueueWrite(questionId, {
      type: 'delete',
    })
  }

  const handleSubmitConfirm = () => {
    setConfirmOpen(false)
    handleSubmit()
  }

  const handleSubmit = async () => {
    if (submissionRef.current) return
    submissionRef.current = true

    try {
      const { timedOut } = await waitForPendingWrites()

      if (timedOut) {
        setPendingWriteMessage(
          'Some answer saves are still pending. If you submit now, those answers might not be recorded.',
        )
        setPendingWriteConfirmOpen(true)
        return
      }

      const response = await studentService.submitAttempt(attemptId)

      setSubmissionState(response.status || 'submitted')
      setFinalStatus(response.status || 'submitted')
      setFinalResult(response.result || null)
      toast.success(
        response.status === 'timed_out'
          ? 'Time expired. Your examination has ended.'
          : 'Examination submitted successfully.',
      )
    } catch (err) {
      submissionRef.current = false
      toast.error(err.message || 'Could not submit the examination.')
    }
  }

  const handleAutoSubmit = async () => {
    if (submissionRef.current || isFinalized()) return
    submissionRef.current = true
    setSubmissionState('submitting')

    try {
      const { timedOut } = await waitForPendingWrites()

      const response = await studentService.submitAttempt(attemptId)

      setSubmissionState(response.status || 'timed_out')
      setFinalStatus(response.status || 'timed_out')
      setFinalResult(response.result || null)

      if (timedOut) {
        toast.error(
          'Time expired. Your examination has ended. Some pending answers may not have been saved.',
        )
      } else {
        toast.error('Time expired. Your examination has ended.')
      }
    } catch (err) {
      submissionRef.current = false
      setSubmissionState('idle')
      toast.error(err.message || 'Could not submit the examination.')
    }
  }

  const handlePendingWriteConfirm = async () => {
    setPendingWriteConfirmOpen(false)
    try {
      const response = await studentService.submitAttempt(attemptId)
      setSubmissionState(response.status || 'submitted')
      setFinalStatus(response.status || 'submitted')
      setFinalResult(response.result || null)
      toast.success(
        response.status === 'timed_out'
          ? 'Time expired. Your examination has ended.'
          : 'Examination submitted successfully.',
      )
    } catch (err) {
      submissionRef.current = false
      toast.error(err.message || 'Could not submit the examination.')
    }
  }

  const handlePendingWriteCancel = () => {
    setPendingWriteConfirmOpen(false)
    submissionRef.current = false
  }

  const answeredCount = Object.values(answers).filter(
    (a) => a.selectedOptionId !== null,
  ).length
  const unansweredCount = questions.length - answeredCount
  const isLowTime = remainingSeconds !== null && remainingSeconds <= 60 && remainingSeconds > 0
  const showTimer = deadline !== null && remainingSeconds !== null

  if (loading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center min-h-screen bg-[var(--color-background)]">
          <Spinner size="lg" />
        </div>
      </AppLayout>
    )
  }

  if (error) {
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

  if (isFinalized()) {
    const statusMessage =
      finalStatus === 'timed_out'
        ? 'Time expired. Your examination has ended.'
        : 'Examination submitted successfully.'

    return (
      <AppLayout>
        <div className="space-y-6">
          <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
            <div>
              <LinkBack onClick={handleBack}>
                ← Return to Dashboard
              </LinkBack>
              <h1 className="page-title mt-2">Examination Ended</h1>
              <p className="text-xs text-[var(--color-text-muted)]">
                Attempt ID: {attemptId}
              </p>
            </div>
            <Badge
              variant={finalStatus === 'timed_out' ? 'danger' : 'primary'}
            >
              {finalStatus === 'timed_out' ? 'Timed Out' : 'Submitted'}
            </Badge>
          </div>

          <Card className="max-w-md">
            <p className="text-sm mb-4">{statusMessage}</p>
            {finalResult && (
              <div className="space-y-2">
                <p className="text-xs text-[var(--color-text-muted)] mb-2">
                  Results
                </p>
                <p className="text-sm">
                  Score: <span className="font-semibold">{finalResult.score}</span> /
                  {finalResult.total_marks}
                </p>
                <p className="text-sm">
                  Percentage:{' '}
                  <span className="font-semibold">{finalResult.percentage}%</span>
                </p>
                <p className="text-sm">
                  Correct: {finalResult.correct_count} | Incorrect: {' '}
                  {finalResult.incorrect_count} | Unanswered:{' '}
                  {finalResult.unanswered_count}
                </p>
              </div>
            )}
          </Card>

          <Button variant="secondary" onClick={handleBack} fullWidth>
            Return to Dashboard
          </Button>
        </div>
      </AppLayout>
    )
  }

  if (!questions || questions.length === 0) {
    return (
      <AppLayout>
        <EmptyState
          icon="📝"
          title="No Questions"
          description="This examination does not have any questions available."
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
            <h1 className="page-title mt-2">Examination</h1>
            <p className="text-xs text-[var(--color-text-muted)]">
              Attempt ID: {attemptId}
            </p>
          </div>
          <div className="flex items-center gap-3">
            {showTimer && (
              <Badge
                variant={isLowTime ? 'danger' : 'primary'}
                className={isLowTime ? 'animate-pulse' : ''}
              >
                ⏰ {formatCountdown(remainingSeconds)}
              </Badge>
            )}
            <Button
              variant="primary"
              size="sm"
              onClick={() => setConfirmOpen(true)}
              disabled={submissionState === 'submitting'}
              loading={submissionState === 'submitting'}
            >
              Submit Examination
            </Button>
          </div>
        </div>

        <div className="space-y-6">
          {questions.map((question) => {
            const questionId = question.id
            const answer = answers[questionId] || {}
            const selectedOptionId = answer.selectedOptionId
            const marked = answer.isMarkedForReview === true
            const saving = isSaving(questionId)
            const saveError = saveErrors[questionId]
            const disabled = isFinalized() || saving || submissionRef.current

            return (
              <Card key={question.id} className="max-w-3xl">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h2 className="text-lg font-bold text-[var(--color-text-primary)] mb-1">
                      {question.question_text}
                    </h2>
                    <p className="text-xs text-[var(--color-text-muted)]">
                      Marks: {question.marks}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant="primary">Question {question.order_index + 1}</Badge>
                    <Button
                      variant={marked ? 'mint' : 'ghost'}
                      size="sm"
                      onClick={() => handleToggleReview(questionId)}
                      disabled={disabled}
                      aria-label={marked ? 'Unmark for review' : 'Mark for review'}
                    >
                      {marked ? '🔖 Review' : 'Review'}
                    </Button>
                    {saveError && (
                      <Badge variant="danger" className="text-[var(--color-text-primary)]">
                        Save error
                      </Badge>
                    )}
                  </div>
                </div>

                <div className="space-y-3">
                  {question.options.map((option) => (
                    <Button
                      key={option.id}
                      variant={isSelected(questionId, option.id) ? 'primary' : 'ghost'}
                      size="md"
                      fullWidth
                      className="justify-start text-left"
                      onClick={() => handleSelectOption(questionId, option.id)}
                      disabled={isSelected(questionId, option.id) || disabled}
                      loading={saving && isSelected(questionId, option.id)}
                    >
                      <span className="font-mono font-semibold mr-2">
                        {option.label}
                      </span>
                      {option.option_text}
                    </Button>
                  ))}
                </div>

                {selectedOptionId !== null && (
                  <Button
                    variant="danger"
                    size="sm"
                    className="mt-3 w-auto"
                    onClick={() => handleClearAnswer(questionId)}
                    disabled={disabled}
                    loading={saving && selectedOptionId !== null}
                  >
                    Clear answer
                  </Button>
                )}
              </Card>
            )
          })}
        </div>

        <p className="text-xs text-[var(--color-text-muted)] text-center">
          Selections are saved automatically. Mark questions you want to review later.
        </p>

        <Modal
          isOpen={confirmOpen}
          onClose={() => setConfirmOpen(false)}
          title="Submit Examination"
          size="md"
        >
          <p className="text-sm mb-4">
            Submitting will end your examination. You will not be able to change
            any answers afterward.
          </p>
          <p className="text-sm mb-4">
            Answered: <span className="font-semibold">{answeredCount}</span> of{' '}
            <span className="font-semibold">{questions.length}</span> questions.
          </p>
          <div className="flex justify-end gap-3">
            <Button variant="secondary" size="sm" onClick={() => setConfirmOpen(false)}>
              Cancel
            </Button>
            <Button
              variant="danger"
              size="sm"
              onClick={handleSubmitConfirm}
              disabled={submissionState === 'submitting'}
              loading={submissionState === 'submitting'}
            >
              Confirm Submit
            </Button>
          </div>
        </Modal>

        <Modal
          isOpen={pendingWriteConfirmOpen}
          onClose={() => setPendingWriteConfirmOpen(false)}
          title="Some answers may not be saved"
          size="md"
        >
          <p className="text-sm mb-4">{pendingWriteMessage}</p>
          <div className="flex justify-end gap-3">
            <Button
              variant="secondary"
              size="sm"
              onClick={handlePendingWriteCancel}
            >
              Cancel
            </Button>
            <Button
              variant="danger"
              size="sm"
              onClick={handlePendingWriteConfirm}
              disabled={submissionState === 'submitting'}
              loading={submissionState === 'submitting'}
            >
              Submit Anyway
            </Button>
          </div>
        </Modal>
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
