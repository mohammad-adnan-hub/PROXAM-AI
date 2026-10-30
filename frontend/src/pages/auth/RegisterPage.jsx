import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import AuthLayout from '../../components/layout/AuthLayout'
import Button from '../../components/shared/Button'
import Input from '../../components/shared/Input'
import { ROUTES } from '../../utils/constants'

export default function RegisterPage() {
  const { user: currentUser, register } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({
    fullName: '',
    email: '',
    password: '',
    confirmPassword: '',
    role: 'student',
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (currentUser) {
      if (currentUser.role === 'student') navigate(ROUTES.STUDENT_DASHBOARD, { replace: true })
      else if (currentUser.role === 'teacher') navigate(ROUTES.TEACHER_DASHBOARD, { replace: true })
      else navigate(ROUTES.ADMIN_DASHBOARD, { replace: true })
    }
  }, [currentUser, navigate])

  const handleChange = (e) => setForm((f) => ({ ...f, [e.target.name]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    if (!form.fullName || !form.email || !form.password) {
      setError('All fields are required.')
      return
    }
    if (form.password.length < 8) {
      setError('Password must be at least 8 characters.')
      return
    }
    if (form.password !== form.confirmPassword) {
      setError('Passwords do not match.')
      return
    }
    setLoading(true)
    try {
      const user = await register(form.fullName, form.email, form.password, form.role)
      if (user.role === 'student') navigate(ROUTES.STUDENT_DASHBOARD, { replace: true })
      else navigate(ROUTES.TEACHER_DASHBOARD, { replace: true })
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <AuthLayout>
      <div className="bg-[var(--color-surface)] rounded-xl p-8 shadow-card border border-[var(--color-border)]">
        <div className="flex flex-col items-center mb-6 text-center">
          <div className="w-12 h-12 rounded-xl bg-[var(--color-primary)] flex items-center justify-center mb-3 shadow-sm">
            <span className="font-display font-extrabold text-[var(--color-mint)] text-xl">P</span>
          </div>
          <h1 className="text-2xl font-display font-bold text-[var(--color-text-primary)]">
            Create your account
          </h1>
          <p className="text-xs text-[var(--color-text-secondary)] mt-1">
            Join Proxam AI as an academic learner or educator
          </p>
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div className="flex gap-2 p-1 bg-[var(--color-surface-soft)] rounded-lg border border-[var(--color-border)]">
            {['student', 'teacher'].map((r) => (
              <button
                key={r}
                type="button"
                onClick={() => setForm((f) => ({ ...f, role: r }))}
                className={[
                  'flex-1 py-2 rounded-md text-xs font-semibold transition-all capitalize',
                  form.role === r
                    ? 'bg-[var(--color-surface)] shadow-sm text-[var(--color-text-primary)]'
                    : 'text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]',
                ].join(' ')}
              >
                {r === 'student' ? 'Student' : 'Teacher / Faculty'}
              </button>
            ))}
          </div>

          <Input
            label="Full Name"
            name="fullName"
            value={form.fullName}
            onChange={handleChange}
            placeholder="Dr. Eleanor Vance or Sarah Jenkins"
            required
          />

          <Input
            label="Institutional Email"
            name="email"
            type="email"
            value={form.email}
            onChange={handleChange}
            placeholder="name@university.edu"
            required
            autoComplete="email"
          />

          <Input
            label="Password"
            name="password"
            type="password"
            value={form.password}
            onChange={handleChange}
            placeholder="Min. 8 characters"
            required
            helperText="At least 8 characters"
            autoComplete="new-password"
          />

          <Input
            label="Confirm Password"
            name="confirmPassword"
            type="password"
            value={form.confirmPassword}
            onChange={handleChange}
            placeholder="Re-enter your password"
            required
            autoComplete="new-password"
          />

          {error && (
            <div className="text-xs text-[var(--color-danger)] bg-[var(--color-danger)]/10 px-3.5 py-2.5 rounded-lg border border-[var(--color-danger)]/20">
              {error}
            </div>
          )}

          <Button type="submit" fullWidth loading={loading} className="mt-1">
            Create Account →
          </Button>
        </form>

        <div className="mt-6 pt-5 border-t border-[var(--color-border)] text-center">
          <p className="text-xs text-[var(--color-text-secondary)]">
            Already registered?{' '}
            <Link to={ROUTES.LOGIN} className="font-semibold text-[var(--color-text-primary)] hover:underline">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </AuthLayout>
  )
}
