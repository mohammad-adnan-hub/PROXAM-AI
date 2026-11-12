import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import AppLayout from '../../components/layout/AppLayout'
import Button from '../../components/shared/Button'
import Card from '../../components/shared/Card'
import Spinner from '../../components/shared/Spinner'
import TestListTable from '../../components/teacher/TestListTable'
import { useToast } from '../../components/shared/Toast'
import { testService } from '../../services/testService'
import { ROUTES } from '../../utils/constants'

export default function TeacherTestsPage() {
  const toast = useToast()
  const [tests, setTests] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const loadTests = async () => {
    setLoading(true)
    setError('')
    try {
      const data = await testService.getTeacherTests()
      setTests(data)
    } catch (err) {
      setError(err.message || 'Unable to load examinations.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadTests()
  }, [])

  return (
    <AppLayout>
      <div className="space-y-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="page-title">My Tests</h1>
            <p className="text-sm text-[var(--color-text-secondary)] mt-1">
              Examinations you have published, with generated access codes.
            </p>
          </div>
          <Link to={ROUTES.TEACHER_CREATE_DETAILS}>
            <Button>+ Create New Test</Button>
          </Link>
        </div>

        {loading && (
          <div className="flex justify-center py-16">
            <Spinner size="lg" />
          </div>
        )}

        {!loading && error && (
          <Card>
            <p className="text-sm mb-3">{error}</p>
            <Button size="sm" variant="secondary" onClick={loadTests}>
              Retry
            </Button>
          </Card>
        )}

        {!loading && !error && (
          <Card className={tests.length ? 'p-0 overflow-hidden' : ''}>
            <div className={tests.length ? 'p-6' : ''}>
              <TestListTable
                tests={tests}
                onCopied={(code) =>
                  code ? toast.success(`Copied ${code}`) : toast.error('Could not copy code')
                }
              />
            </div>
          </Card>
        )}
      </div>
    </AppLayout>
  )
}
