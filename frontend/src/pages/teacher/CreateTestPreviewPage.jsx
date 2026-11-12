import { useState } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import AppLayout from '../../components/layout/AppLayout'
import Badge from '../../components/shared/Badge'
import Button from '../../components/shared/Button'
import Card from '../../components/shared/Card'
import WizardStepper from '../../components/teacher/WizardStepper'
import { useTestCreation } from '../../context/TestCreationContext'
import { useToast } from '../../components/shared/Toast'
import { testService } from '../../services/testService'
import { ROUTES } from '../../utils/constants'
import { formatDuration, teacherTestPath } from '../../utils/formatters'

export default function CreateTestPreviewPage() {
  const navigate = useNavigate()
  const toast = useToast()
  const { draft, resetDraft, isBasicInfoValid, isQuestionsValid } = useTestCreation()
  const [publishing, setPublishing] = useState(false)

  if (!isBasicInfoValid()) {
    return <Navigate to={ROUTES.TEACHER_CREATE_DETAILS} replace />
  }
  if (!isQuestionsValid()) {
    return <Navigate to={ROUTES.TEACHER_CREATE_QUESTIONS} replace />
  }

  const totalMarks = draft.questions.reduce((sum, q) => sum + Number(q.marks || 0), 0)

  const handlePublish = async () => {
    setPublishing(true)
    try {
      const created = await testService.createTest({
        title: draft.title.trim(),
        description: draft.description?.trim() || null,
        instructions: draft.instructions?.trim() || null,
        duration_minutes: Number(draft.duration_minutes),
        questions: draft.questions.map((q, index) => ({
          question_text: q.question_text.trim(),
          marks: Number(q.marks),
          order_index: index,
          options: q.options.map((opt) => ({
            label: opt.label,
            option_text: opt.option_text.trim(),
            is_correct: Boolean(opt.is_correct),
          })),
        })),
      })
      resetDraft()
      toast.success('Examination published')
      navigate(teacherTestPath(ROUTES.TEACHER_TEST_SUCCESS, created.id), { replace: true })
    } catch (err) {
      toast.error(err.message || 'Could not publish examination')
    } finally {
      setPublishing(false)
    }
  }

  return (
    <AppLayout>
      <div className="space-y-6">
        <Link to={ROUTES.TEACHER_CREATE_QUESTIONS} className="text-sm text-[var(--color-text-secondary)]">
          ← Back to questions
        </Link>
        <WizardStepper current={3} />

        <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
          <div>
            <h1 className="page-title">{draft.title}</h1>
            <p className="text-sm text-[var(--color-text-secondary)] mt-1">
              {formatDuration(draft.duration_minutes)} · {draft.questions.length} questions · {totalMarks} marks
            </p>
          </div>
          <Button loading={publishing} onClick={handlePublish}>
            Publish examination
          </Button>
        </div>

        {draft.description && (
          <Card>
            <h2 className="text-sm font-bold mb-2">Description</h2>
            <p className="text-sm whitespace-pre-wrap text-[var(--color-text-secondary)]">{draft.description}</p>
          </Card>
        )}

        {draft.instructions && (
          <Card>
            <h2 className="text-sm font-bold mb-2">Instructions</h2>
            <p className="text-sm whitespace-pre-wrap text-[var(--color-text-secondary)]">{draft.instructions}</p>
          </Card>
        )}

        <div className="space-y-4">
          {draft.questions.map((question, index) => (
            <Card key={index}>
              <div className="flex justify-between gap-4 mb-3">
                <h3 className="font-semibold text-sm">
                  {index + 1}. {question.question_text}
                </h3>
                <Badge variant="mint">{question.marks} marks</Badge>
              </div>
              <ul className="space-y-2">
                {question.options.map((opt) => (
                  <li
                    key={opt.label}
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

        <div className="flex justify-between pb-8">
          <Link to={ROUTES.TEACHER_CREATE_QUESTIONS}>
            <Button variant="secondary">← Edit questions</Button>
          </Link>
          <Button loading={publishing} onClick={handlePublish}>
            Publish examination
          </Button>
        </div>
      </div>
    </AppLayout>
  )
}
