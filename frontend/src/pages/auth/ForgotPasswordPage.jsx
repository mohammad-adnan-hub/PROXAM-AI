import { useState } from 'react'
import { Link } from 'react-router-dom'
import { authService } from '../../services/authService'
import AuthLayout from '../../components/layout/AuthLayout'
import Button from '../../components/shared/Button'
import Input from '../../components/shared/Input'
import { ROUTES } from '../../utils/constants'

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('')
  const [submitted, setSubmitted] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    if (!email) {
      setError('Please enter your email address.')
      return
    }
    setLoading(true)
    try {
      await authService.forgotPassword(email)
      setSubmitted(true)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <AuthLayout>
      <div className="bg-[var(--color-surface)] rounded-xl p-8 shadow-card border border-[var(--color-border)]">
        <h1 className="text-2xl font-display font-bold mb-2">Reset your password</h1>
        <p className="text-xs text-[var(--color-text-secondary)] mb-6">
          Enter your registered email address. If an account is found, a secure single-use link will be sent.
        </p>

        {submitted ? (
          <div className="bg-[var(--color-mint)]/40 border border-[var(--color-mint-strong)] rounded-xl p-5 text-xs text-[var(--color-text-primary)] leading-relaxed">
            <p className="font-bold mb-1">Check your email</p>
            <p>
              If an account with <strong>{email}</strong> exists, a password reset link has been dispatched.
              The link will expire in 30 minutes. In local dev mode, the link is logged directly to the backend terminal.
            </p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <Input
              label="Email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="name@university.edu"
              required
            />
            {error && (
              <div className="text-xs text-[var(--color-danger)] bg-[var(--color-danger)]/10 px-3 py-2 rounded-md">
                {error}
              </div>
            )}
            <Button type="submit" fullWidth loading={loading}>
              Send Reset Link
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
