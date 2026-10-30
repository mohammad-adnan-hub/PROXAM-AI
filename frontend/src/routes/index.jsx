import { Routes, Route, Navigate } from 'react-router-dom'
import { Suspense, lazy } from 'react'
import ProtectedRoute from './ProtectedRoute'
import Spinner from '../components/shared/Spinner'
import { ROUTES } from '../utils/constants'

// Lazy-loaded pages
const LandingPage = lazy(() => import('../pages/public/LandingPage'))
const AboutPage = lazy(() => import('../pages/public/AboutPage'))
const HelpPage = lazy(() => import('../pages/public/HelpPage'))
const LoginPage = lazy(() => import('../pages/auth/LoginPage'))
const RegisterPage = lazy(() => import('../pages/auth/RegisterPage'))
const ForgotPasswordPage = lazy(() => import('../pages/auth/ForgotPasswordPage'))
const ResetPasswordPage = lazy(() => import('../pages/auth/ResetPasswordPage'))

const StudentDashboard = lazy(() => import('../pages/student/StudentDashboard'))
const TeacherDashboard = lazy(() => import('../pages/teacher/TeacherDashboard'))
const AdminDashboard = lazy(() => import('../pages/admin/AdminDashboard'))

const NotFoundPage = lazy(() => import('../pages/NotFoundPage'))
const UnauthorizedPage = lazy(() => import('../pages/UnauthorizedPage'))

const PageLoader = () => (
  <div className="flex items-center justify-center min-h-screen bg-[var(--color-background)]">
    <Spinner size="lg" />
  </div>
)

export default function AppRoutes() {
  return (
    <Suspense fallback={<PageLoader />}>
      <Routes>
        {/* Public */}
        <Route path={ROUTES.HOME} element={<LandingPage />} />
        <Route path={ROUTES.ABOUT} element={<AboutPage />} />
        <Route path={ROUTES.HELP} element={<HelpPage />} />

        {/* Auth */}
        <Route path={ROUTES.LOGIN} element={<LoginPage />} />
        <Route path={ROUTES.REGISTER} element={<RegisterPage />} />
        <Route path={ROUTES.FORGOT_PASSWORD} element={<ForgotPasswordPage />} />
        <Route path={ROUTES.RESET_PASSWORD} element={<ResetPasswordPage />} />

        {/* Student Routes */}
        <Route
          path="/student/*"
          element={
            <ProtectedRoute roles={['student']}>
              <StudentDashboard />
            </ProtectedRoute>
          }
        />

        {/* Teacher Routes */}
        <Route
          path="/teacher/*"
          element={
            <ProtectedRoute roles={['teacher']}>
              <TeacherDashboard />
            </ProtectedRoute>
          }
        />

        {/* Admin Routes */}
        <Route
          path="/admin/*"
          element={
            <ProtectedRoute roles={['admin']}>
              <AdminDashboard />
            </ProtectedRoute>
          }
        />

        {/* System Error & Fallback Routes */}
        <Route path={ROUTES.UNAUTHORIZED} element={<UnauthorizedPage />} />
        <Route path={ROUTES.NOT_FOUND} element={<NotFoundPage />} />
        <Route path="*" element={<Navigate to={ROUTES.NOT_FOUND} replace />} />
      </Routes>
    </Suspense>
  )
}
