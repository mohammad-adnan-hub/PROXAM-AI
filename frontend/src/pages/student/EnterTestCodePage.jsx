import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import AppLayout from '../../components/layout/AppLayout'
import Button from '../../components/shared/Button'
import Card from '../../components/shared/Card'
import EmptyState from '../../components/shared/EmptyState'
import Input from '../../components/shared/Input'
import Spinner from '../../components/shared/Spinner'
import { useToast } from '../../components/shared/Toast'
import { useAuth } from '../../context/AuthContext'
import { studentService } from '../../services/studentService'
import { ROUTES } from '../../utils/constants'

export default function EnterTestCodePage() {
  const navigate = useNavigate()
  const toast = useToast()
  const { user } = useAuth()
  const [testCode, setTestCode] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const data = await studentService.validateTestCode(testCode.trim())
      toast.success('Examination code validated')
      navigate(ROUTES.STUDENT_TEST_DETAILS.replace(':testId', String(data.id)))
    } catch (err) {
      setError(err.message || 'Invalid test code. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center min-h-screen bg-[var(--color-background)]">
          <Spinner size="lg" />
        </div>
      </AppLayout>
    )
  }

  return (
    <AppLayout>
      <div className="space-y-8">
        <div>
          <span className="text-xs font-semibold text-[var(--color-text-muted)] uppercase tracking-wider">
            Student Access
          </span>
          <h1 className="page-title mt-1">Enter Examination Code</h1>
          <p className="text-[var(--color-text-secondary)] text-sm mt-1">
            Welcome back, {user?.full_name}. Enter the test code provided by your teacher to access your examination.
          </p>
        </div>

        <Card className="max-w-lg">
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              label="Test Code"
              placeholder="e.g. PXAM-7K4Q2"
              value={testCode}
              onChange={(e) => setTestCode(e.target.value)}
              error={!!error}
              helperText={error || 'Enter the 10-character examination code provided by your teacher'}
              required
            />
            <Button
              type="submit"
              size="lg"
              fullWidth
              loading={loading}
              disabled={loading || !testCode.trim()}
            >
              Validate Code →
            </Button>
          </form>
        </Card>

        <EmptyState
          icon="📋"
          title="No test code yet?"
          description="Ask your teacher for an examination code. They will share a unique code (e.g. PXAM-7K4Q2) that you can enter here to begin your assessment."
          action={
            <Button variant="secondary" size="sm">
              Return to Dashboard
            </Button>
          }
        />
      </div>
    </AppLayout>
  )
}
