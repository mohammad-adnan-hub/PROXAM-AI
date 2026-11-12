import { Link } from 'react-router-dom'
import Badge from '../shared/Badge'
import Button from '../shared/Button'
import EmptyState from '../shared/EmptyState'
import { ROUTES } from '../../utils/constants'
import { copyToClipboard, formatDate, formatDuration, teacherTestPath } from '../../utils/formatters'

const statusVariant = {
  active: 'success',
  draft: 'warning',
  closed: 'default',
}

export default function TestListTable({ tests, onCopied, createAction }) {
  if (!tests?.length) {
    return (
      <EmptyState
        icon="📂"
        title="No Examinations Authored Yet"
        description="Create your first multiple-choice assessment. Proxam AI will generate a unique 10-character code automatically."
        action={
          createAction || (
            <Link to={ROUTES.TEACHER_CREATE_DETAILS}>
              <Button size="sm">Create First Examination</Button>
            </Link>
          )
        }
      />
    )
  }

  const handleCopy = async (code) => {
    try {
      await copyToClipboard(code)
      onCopied?.(code)
    } catch {
      onCopied?.(null)
    }
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm text-left">
        <thead>
          <tr className="text-[11px] uppercase tracking-wider text-[var(--color-text-muted)] border-b border-[var(--color-border)]">
            <th className="py-3 pr-4 font-semibold">Title</th>
            <th className="py-3 pr-4 font-semibold">Code</th>
            <th className="py-3 pr-4 font-semibold">Questions</th>
            <th className="py-3 pr-4 font-semibold">Duration</th>
            <th className="py-3 pr-4 font-semibold">Created</th>
            <th className="py-3 pr-4 font-semibold">Attempts</th>
            <th className="py-3 pr-4 font-semibold">Status</th>
            <th className="py-3 font-semibold">Actions</th>
          </tr>
        </thead>
        <tbody>
          {tests.map((test) => (
            <tr key={test.id} className="border-b border-[var(--color-border)] last:border-0">
              <td className="py-3 pr-4 font-medium">{test.title}</td>
              <td className="py-3 pr-4 font-mono text-xs">{test.test_code}</td>
              <td className="py-3 pr-4">{test.question_count}</td>
              <td className="py-3 pr-4">{formatDuration(test.duration_minutes)}</td>
              <td className="py-3 pr-4">{formatDate(test.created_at)}</td>
              <td className="py-3 pr-4">{test.attempt_count}</td>
              <td className="py-3 pr-4">
                <Badge variant={statusVariant[test.status] || 'default'}>{test.status}</Badge>
              </td>
              <td className="py-3">
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    className="text-xs font-semibold underline"
                    onClick={() => handleCopy(test.test_code)}
                  >
                    Copy
                  </button>
                  <Link
                    to={teacherTestPath(ROUTES.TEACHER_TEST_DETAILS, test.id)}
                    className="text-xs font-semibold underline"
                  >
                    View
                  </Link>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
