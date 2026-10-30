import { useState, useEffect } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { authService } from '../../services/authService'
import AuthLayout from '../../components/layout/AuthLayout'
import Button from '../../components/shared/Button'
import Input from '../../components/shared/Input'
import { ROUTES } from '../../utils/constants'

export default function ResetPasswordPage() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const token = searchParams.get('token') || ''
  const [form, setForm] = useState({ password: '', confirm: '' })
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!token) {
      setError('Invalid or missing reset token. Please request a new password reset link.')
    }
  }, [token])

  const handleChange = (e) => setForm((f) => ({ ...f, [e.target.name]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    if (form.password.length < 8) {
      setError('Password must be at least 8 characters.')
      return
    }
    if (form.password !== form.confirm) {
      setError('Passwords do not match.')
      return
    }
    setLoading(true)
    try {
      await authService.resetPassword(token, form.password)
      setSuccess(true)
      setTimeout(() => navigate(ROUTES.LOGIN), 2500)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <AuthLayout>
      <div className="bg-[var(--color-surface)] rounded-xl p-8 shadow-card border border-[var(--color-border)]">
        <h1 className="text-2xl font-display font-bold mb-2">Set new password</h1>
        <p className="text-xs text-[var(--color-text-secondary)] mb-6">
          Enter and confirm your new secure account password.
        </p>

        {success ? (
          <div className="bg-[var(--color-mint)]/40 border border-[var(--color-mint-strong)] rounded-xl p-5 text-xs text-[var(--color-text-primary)]">
            <p className="font-bold mb-1">Password reset successfully!</p>
            <p>Your password has been changed. Redirecting to sign in...</p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <Input
              label="New Password"
              name="password"
              type="password"
              value={form.password}
              onChange={handleChange}
              placeholder="Min. 8 characters"
              required
              helperText="Minimum 8 characters"
            />
            <Input
              label="Confirm New Password"
              name="confirm"
              type="password"
              value={form.confirm}
              onChange={handleChange}
              placeholder="Re-enter password"
              required
            />
            {error && (
              <div className="text-xs text-[var(--color-danger)] bg-[var(--color-danger)]/10 px-3 py-2 rounded-md">
                {error}
              </div>
            )}
            <Button type="submit" fullWidth loading={loading} disabled={!token}>
              Update Password
            </Button>
          </form>
        )}

        <div className="mt-6 pt-5 border-t border-[var(--color-border)] text-center">
          <Link to={ROUTES.LOGIN} className="text-xs font-semibold text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]">
            ← Return to sign in
          </Link>
        </div>
      </div>
    </AuthLayout>
  )
}
