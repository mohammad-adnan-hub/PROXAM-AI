import { useState, useEffect } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import AuthLayout from '../../components/layout/AuthLayout'
import Button from '../../components/shared/Button'
import Input from '../../components/shared/Input'
import { ROUTES } from '../../utils/constants'

export default function LoginPage() {
  const { user: currentUser, login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [form, setForm] = useState({ email: '', password: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)

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
    if (!form.email || !form.password) {
      setError('Please enter your email and password.')
      return
    }
    setLoading(true)
    try {
      const user = await login(form.email, form.password)
      const from = location.state?.from?.pathname
      if (from && !['/login', '/register', '/unauthorized'].includes(from)) {
        navigate(from, { replace: true })
        return
      }
      if (user.role === 'student') navigate(ROUTES.STUDENT_DASHBOARD, { replace: true })
      else if (user.role === 'teacher') navigate(ROUTES.TEACHER_DASHBOARD, { replace: true })
      else navigate(ROUTES.ADMIN_DASHBOARD, { replace: true })
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
          <h1 className="text-2xl font-display font-bold text-[var(--color-text-primary)]">Welcome to Proxam AI</h1>
          <p className="text-xs text-[var(--color-text-secondary)] mt-1">
            Sign in to access your assessment workspace
          </p>
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
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

          <div className="relative">
            <Input
              label="Password"
              name="password"
              type={showPassword ? 'text' : 'password'}
              value={form.password}
              onChange={handleChange}
              placeholder="••••••••"
              required
              autoComplete="current-password"
            />
            <button
              type="button"
              onClick={() => setShowPassword((v) => !v)}
              className="absolute right-3 top-[38px] text-[var(--color-text-muted)] hover:text-[var(--color-text-primary)] text-xs font-semibold"
            >
              {showPassword ? 'Hide' : 'Show'}
            </button>
          </div>

          {error && (
            <div className="text-xs text-[var(--color-danger)] bg-[var(--color-danger)]/10 px-3.5 py-2.5 rounded-lg border border-[var(--color-danger)]/20">
              {error}
            </div>
          )}

          <div className="flex justify-end">
            <Link
              to={ROUTES.FORGOT_PASSWORD}
              className="text-xs font-medium text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] transition-colors"
            >
              Forgot password?
            </Link>
          </div>

          <Button type="submit" fullWidth loading={loading} className="mt-1">
            Sign In to Workspace →
          </Button>
        </form>

        <div className="mt-6 pt-5 border-t border-[var(--color-border)] text-center">
          <p className="text-xs text-[var(--color-text-secondary)]">
            New to Proxam AI?{' '}
            <Link to={ROUTES.REGISTER} className="font-semibold text-[var(--color-text-primary)] hover:underline">
              Create an account
            </Link>
          </p>
        </div>
      </div>
    </AuthLayout>
  )
}
