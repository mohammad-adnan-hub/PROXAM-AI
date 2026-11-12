import Input from '../shared/Input'
import Button from '../shared/Button'

export function blankQuestion() {
  return {
    question_text: '',
    marks: 1,
    options: [
      { label: 'A', option_text: '', is_correct: true },
      { label: 'B', option_text: '', is_correct: false },
      { label: 'C', option_text: '', is_correct: false },
      { label: 'D', option_text: '', is_correct: false },
    ],
  }
}

export default function QuestionEditor({
  index,
  question,
  total,
  onChange,
  onDelete,
  onMoveUp,
  onMoveDown,
}) {
  const updateField = (field, value) => {
    onChange({ ...question, [field]: value })
  }

  const updateOption = (optIndex, patch) => {
    const options = question.options.map((opt, i) => {
      if (i !== optIndex) {
        return patch.is_correct ? { ...opt, is_correct: false } : opt
      }
      return { ...opt, ...patch }
    })
    onChange({ ...question, options })
  }

  return (
    <div className="bg-[var(--color-surface)] rounded-lg p-6 shadow-card border border-[var(--color-border)] relative overflow-hidden">
      <div className="absolute left-0 top-0 bottom-0 w-1.5 bg-[var(--color-mint)]" />
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
        <h3 className="font-semibold text-sm">Question {index + 1}</h3>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={onMoveUp}
            disabled={index === 0}
            className="px-2.5 py-1.5 text-xs rounded-lg border border-[var(--color-border)] disabled:opacity-40"
          >
            Up
          </button>
          <button
            type="button"
            onClick={onMoveDown}
            disabled={index === total - 1}
            className="px-2.5 py-1.5 text-xs rounded-lg border border-[var(--color-border)] disabled:opacity-40"
          >
            Down
          </button>
          <Button variant="danger" size="sm" onClick={onDelete}>
            Delete
          </Button>
        </div>
      </div>

      <div className="flex flex-col gap-4">
        <div className="flex flex-col gap-1.5">
          <label className="text-sm font-medium" htmlFor={`q-text-${index}`}>
            Question text <span className="text-[var(--color-danger)]">*</span>
          </label>
          <textarea
            id={`q-text-${index}`}
            rows={3}
            value={question.question_text}
            onChange={(e) => updateField('question_text', e.target.value)}
            className="w-full px-4 py-3 rounded-md border border-[var(--color-border)] bg-[var(--color-surface)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
            placeholder="Enter the question students will see"
          />
        </div>

        <div className="max-w-[160px]">
          <Input
            label="Marks"
            type="number"
            min="0"
            step="0.5"
            value={question.marks}
            onChange={(e) => updateField('marks', Number(e.target.value))}
          />
        </div>

        <fieldset className="flex flex-col gap-3">
          <legend className="text-sm font-medium mb-1">
            Options (select exactly one correct answer)
          </legend>
          {question.options.map((opt, optIndex) => (
            <label
              key={opt.label}
              className={[
                'flex items-start gap-3 p-3 rounded-md border',
                opt.is_correct
                  ? 'border-[var(--color-mint-strong)] bg-[var(--color-mint)]/30'
                  : 'border-[var(--color-border)]',
              ].join(' ')}
            >
              <input
                type="radio"
                name={`correct-${index}`}
                checked={opt.is_correct}
                onChange={() => updateOption(optIndex, { is_correct: true })}
                className="mt-3"
              />
              <span className="w-7 h-7 mt-1.5 rounded-full bg-[var(--color-surface-soft)] flex items-center justify-center text-xs font-bold shrink-0">
                {opt.label}
              </span>
              <input
                type="text"
                value={opt.option_text}
                onChange={(e) => updateOption(optIndex, { option_text: e.target.value })}
                placeholder={`Option ${opt.label}`}
                className="flex-1 min-h-[44px] px-3 rounded-md border border-[var(--color-border)] bg-[var(--color-surface)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
              />
            </label>
          ))}
        </fieldset>
      </div>
    </div>
  )
}
