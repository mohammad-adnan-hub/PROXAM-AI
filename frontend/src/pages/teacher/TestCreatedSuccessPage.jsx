import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import AppLayout from '../../components/layout/AppLayout'
import Badge from '../../components/shared/Badge'
import Button from '../../components/shared/Button'
import Card from '../../components/shared/Card'
import Spinner from '../../components/shared/Spinner'
import { useToast } from '../../components/shared/Toast'
import { testService } from '../../services/testService'
import { ROUTES } from '../../utils/constants'
import { copyToClipboard, formatDuration, teacherTestPath } from '../../utils/formatters'

export default function TestCreatedSuccessPage() {
  const { testId } = useParams()
  const toast = useToast()
  const [test, setTest] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const load = async () => {
      try {
        const data = await testService.getTestDetails(testId)
        setTest(data)
      } catch (err) {
        setError(err.message || 'Unable to load the published examination.')
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
          <Link to={ROUTES.TEACHER_DASHBOARD}>
            <Button size="sm">Go to dashboard</Button>
          </Link>
        </Card>
      )}

      {!loading && test && (
        <div className="max-w-xl mx-auto space-y-6 text-center py-6">
          <div className="w-14 h-14 rounded-full bg-[var(--color-mint)] flex items-center justify-center mx-auto text-xl font-bold">
            ✓
          </div>
          <div>
            <h1 className="page-title">Test created successfully</h1>
            <p className="text-sm text-[var(--color-text-secondary)] mt-2">
              Share this code with students so they can enter the examination.
            </p>
          </div>

          <Card>
            <p className="text-sm font-semibold">{test.title}</p>
            <p className="font-mono text-3xl font-bold tracking-wide mt-4">{test.test_code}</p>
            <div className="flex justify-center gap-2 mt-4">
              <Badge variant="success">{test.status}</Badge>
              <Badge>{test.question_count} questions</Badge>
              <Badge>{formatDuration(test.duration_minutes)}</Badge>
            </div>
            <div className="mt-6">
              <Button onClick={handleCopy}>Copy code</Button>
            </div>
          </Card>

          <div className="flex flex-col sm:flex-row justify-center gap-3">
            <Link to={teacherTestPath(ROUTES.TEACHER_TEST_DETAILS, test.id)}>
              <Button variant="secondary">View test details</Button>
            </Link>
            <Link to={ROUTES.TEACHER_DASHBOARD}>
              <Button variant="ghost">Go to dashboard</Button>
            </Link>
          </div>
        </div>
      )}
    </AppLayout>
  )
}
