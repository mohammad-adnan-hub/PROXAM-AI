import { Link, Navigate, useNavigate } from 'react-router-dom'
import AppLayout from '../../components/layout/AppLayout'
import Button from '../../components/shared/Button'
import QuestionEditor, { blankQuestion } from '../../components/teacher/QuestionEditor'
import WizardStepper from '../../components/teacher/WizardStepper'
import { useTestCreation } from '../../context/TestCreationContext'
import { ROUTES } from '../../utils/constants'

export default function CreateTestQuestionsPage() {
  const navigate = useNavigate()
  const {
    draft,
    addQuestion,
    updateQuestion,
    deleteQuestion,
    reorderQuestions,
    isBasicInfoValid,
    isQuestionsValid,
  } = useTestCreation()

  if (!isBasicInfoValid()) {
    return <Navigate to={ROUTES.TEACHER_CREATE_DETAILS} replace />
  }

  const totalMarks = draft.questions.reduce((sum, q) => sum + Number(q.marks || 0), 0)

  return (
    <AppLayout>
      <div className="space-y-6">
        <Link to={ROUTES.TEACHER_CREATE_DETAILS} className="text-sm text-[var(--color-text-secondary)]">
          ← Back to Test Details
        </Link>
        <WizardStepper current={2} />

        <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-4">
          <div>
            <h1 className="page-title">Author multiple-choice questions</h1>
            <p className="text-sm text-[var(--color-text-secondary)] mt-1">
              {draft.title} · {draft.questions.length} question
              {draft.questions.length === 1 ? '' : 's'} · {totalMarks} marks · {draft.duration_minutes} min
            </p>
          </div>
          <Button type="button" variant="secondary" onClick={() => addQuestion(blankQuestion())}>
            + Add question
          </Button>
        </div>

        {draft.questions.length === 0 && (
          <div className="bg-[var(--color-surface)] rounded-lg p-8 text-center border border-[var(--color-border)]">
            <p className="text-sm text-[var(--color-text-secondary)] mb-4">
              Add at least one MCQ with four options and exactly one correct answer.
            </p>
            <Button onClick={() => addQuestion(blankQuestion())}>Add first question</Button>
          </div>
        )}

        <div className="flex flex-col gap-6">
          {draft.questions.map((question, index) => (
            <QuestionEditor
              key={index}
              index={index}
              total={draft.questions.length}
              question={question}
              onChange={(updated) => updateQuestion(index, updated)}
              onDelete={() => deleteQuestion(index)}
              onMoveUp={() => reorderQuestions(index, index - 1)}
              onMoveDown={() => reorderQuestions(index, index + 1)}
            />
          ))}
        </div>

        <div className="flex justify-between pb-8">
          <Link to={ROUTES.TEACHER_CREATE_DETAILS}>
            <Button variant="secondary">← Details</Button>
          </Link>
          <Button
            disabled={!isQuestionsValid()}
            onClick={() => navigate(ROUTES.TEACHER_CREATE_PREVIEW)}
          >
            Continue to preview →
          </Button>
        </div>
      </div>
    </AppLayout>
  )
}
