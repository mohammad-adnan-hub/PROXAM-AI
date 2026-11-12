import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import AppLayout from '../../components/layout/AppLayout'
import Button from '../../components/shared/Button'
import Input from '../../components/shared/Input'
import WizardStepper from '../../components/teacher/WizardStepper'
import { useTestCreation } from '../../context/TestCreationContext'
import { ROUTES } from '../../utils/constants'

export default function CreateTestDetailsPage() {
  const navigate = useNavigate()
  const { draft, updateBasicInfo, isBasicInfoValid } = useTestCreation()
  const [form, setForm] = useState({
    title: draft.title,
    description: draft.description || '',
    instructions: draft.instructions || '',
    duration_minutes: draft.duration_minutes,
  })
  const [error, setError] = useState('')

  const handleChange = (e) => {
    const { name, value } = e.target
    const next = {
      ...form,
      [name]: value,
    }
    setForm(next)
    updateBasicInfo({
      title: next.title,
      description: next.description,
      instructions: next.instructions,
      duration_minutes: Number(next.duration_minutes),
    })
  }

  const handleContinue = (e) => {
    e.preventDefault()
    const duration = Number(form.duration_minutes)
    updateBasicInfo({
      title: form.title,
      description: form.description,
      instructions: form.instructions,
      duration_minutes: duration,
    })
    if (!form.title.trim() || duration < 1 || duration > 600) {
      setError('Enter a title and a duration between 1 and 600 minutes.')
      return
    }
    setError('')
    navigate(ROUTES.TEACHER_CREATE_QUESTIONS)
  }

  return (
    <AppLayout>
      <div className="space-y-6 max-w-3xl">
        <Link to={ROUTES.TEACHER_TESTS} className="text-sm text-[var(--color-text-secondary)]">
          ← Back to Test Records
        </Link>
        <WizardStepper current={1} />

        <form onSubmit={handleContinue} className="bg-[var(--color-surface)] rounded-xl p-6 sm:p-8 shadow-card border border-[var(--color-border)] space-y-5">
          <div>
            <span className="text-[11px] font-semibold uppercase tracking-wider text-[var(--color-text-muted)]">
              Step 01 of 03
            </span>
            <h1 className="page-title mt-2">Enter examination specifications</h1>
            <p className="text-sm text-[var(--color-text-secondary)] mt-1">
              Configure the title, time limit, and student guidelines for this assessment.
            </p>
          </div>

          <Input
            label="Examination title"
            name="title"
            value={form.title}
            onChange={handleChange}
            placeholder="e.g. Midterm Assessment: Algorithms"
            required
          />

          <div className="flex flex-col gap-1.5">
            <label htmlFor="description" className="text-sm font-medium">
              Description
            </label>
            <textarea
              id="description"
              name="description"
              rows={3}
              value={form.description}
              onChange={handleChange}
              className="w-full px-4 py-3 rounded-md border border-[var(--color-border)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
              placeholder="Optional summary shown to students"
            />
          </div>

          <Input
            label="Duration (minutes)"
            name="duration_minutes"
            type="number"
            min="1"
            max="600"
            value={form.duration_minutes}
            onChange={handleChange}
            required
            helperText="Between 1 and 600 minutes"
          />

          <div className="flex flex-col gap-1.5">
            <label htmlFor="instructions" className="text-sm font-medium">
              Instructions
            </label>
            <textarea
              id="instructions"
              name="instructions"
              rows={5}
              value={form.instructions}
              onChange={handleChange}
              className="w-full px-4 py-3 rounded-md border border-[var(--color-border)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
              placeholder="Rules and guidance for candidates"
            />
          </div>

          {error && <p className="text-sm text-[var(--color-danger)]">{error}</p>}

          <div className="flex justify-between pt-2">
            <Link to={ROUTES.TEACHER_DASHBOARD}>
              <Button type="button" variant="secondary">
                Cancel
              </Button>
            </Link>
            <Button type="submit" disabled={!isBasicInfoValid()}>
              Continue to questions →
            </Button>
          </div>
        </form>
      </div>
    </AppLayout>
  )
}
