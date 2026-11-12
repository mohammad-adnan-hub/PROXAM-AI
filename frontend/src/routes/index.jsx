import { Routes, Route, Navigate, Outlet } from 'react-router-dom'
import { Suspense, lazy } from 'react'
import ProtectedRoute from './ProtectedRoute'
import Spinner from '../components/shared/Spinner'
import { ROUTES } from '../utils/constants'
import { TestCreationProvider } from '../context/TestCreationContext'

const LandingPage = lazy(() => import('../pages/public/LandingPage'))
const AboutPage = lazy(() => import('../pages/public/AboutPage'))
const HelpPage = lazy(() => import('../pages/public/HelpPage'))
const LoginPage = lazy(() => import('../pages/auth/LoginPage'))
const RegisterPage = lazy(() => import('../pages/auth/RegisterPage'))
const ForgotPasswordPage = lazy(() => import('../pages/auth/ForgotPasswordPage'))
const ResetPasswordPage = lazy(() => import('../pages/auth/ResetPasswordPage'))

const StudentDashboard = lazy(() => import('../pages/student/StudentDashboard'))
const StudentHistory = lazy(() => import('../pages/student/StudentHistory'))
const EnterTestCodePage = lazy(() => import('../pages/student/EnterTestCodePage'))
const StudentTestDetailsPage = lazy(() => import('../pages/student/StudentTestDetailsPage'))
const StudentPreExamPage = lazy(() => import('../pages/student/StudentPreExamPage'))
const StudentExaminationPage = lazy(() => import('../pages/student/StudentExaminationPage'))
const TeacherDashboard = lazy(() => import('../pages/teacher/TeacherDashboard'))
const TeacherTestsPage = lazy(() => import('../pages/teacher/TeacherTestsPage'))
const TeacherTestDetailsPage = lazy(() => import('../pages/teacher/TeacherTestDetailsPage'))
const CreateTestDetailsPage = lazy(() => import('../pages/teacher/CreateTestDetailsPage'))
const CreateTestQuestionsPage = lazy(() => import('../pages/teacher/CreateTestQuestionsPage'))
const CreateTestPreviewPage = lazy(() => import('../pages/teacher/CreateTestPreviewPage'))
const TestCreatedSuccessPage = lazy(() => import('../pages/teacher/TestCreatedSuccessPage'))
const AdminDashboard = lazy(() => import('../pages/admin/AdminDashboard'))

const NotFoundPage = lazy(() => import('../pages/NotFoundPage'))
const UnauthorizedPage = lazy(() => import('../pages/UnauthorizedPage'))

const PageLoader = () => (
  <div className="flex items-center justify-center min-h-screen bg-[var(--color-background)]">
    <Spinner size="lg" />
  </div>
)

function TeacherGuard() {
  return (
    <ProtectedRoute roles={['teacher']}>
      <Outlet />
    </ProtectedRoute>
  )
}

function TestCreationLayout() {
  return (
    <TestCreationProvider>
      <Outlet />
    </TestCreationProvider>
  )
}

export default function AppRoutes() {
  return (
    <Suspense fallback={<PageLoader />}>
      <Routes>
        <Route path={ROUTES.HOME} element={<LandingPage />} />
        <Route path={ROUTES.ABOUT} element={<AboutPage />} />
        <Route path={ROUTES.HELP} element={<HelpPage />} />

        <Route path={ROUTES.LOGIN} element={<LoginPage />} />
        <Route path={ROUTES.REGISTER} element={<RegisterPage />} />
        <Route path={ROUTES.FORGOT_PASSWORD} element={<ForgotPasswordPage />} />
        <Route path={ROUTES.RESET_PASSWORD} element={<ResetPasswordPage />} />

        <Route path="/student/dashboard" element={<ProtectedRoute roles={['student']}><StudentDashboard /></ProtectedRoute>} />
        <Route path="/student/history" element={<ProtectedRoute roles={['student']}><StudentHistory /></ProtectedRoute>} />
        <Route path="/student/enter-code" element={<ProtectedRoute roles={['student']}><EnterTestCodePage /></ProtectedRoute>} />
        <Route path="/student/tests/:testId" element={<ProtectedRoute roles={['student']}><StudentTestDetailsPage /></ProtectedRoute>} />
        <Route path="/student/attempts/:attemptId/system-check" element={<ProtectedRoute roles={['student']}><StudentPreExamPage /></ProtectedRoute>} />
        <Route path="/student/attempts/:attemptId/exam" element={<ProtectedRoute roles={['student']}><StudentExaminationPage /></ProtectedRoute>} />
        <Route path="/student/*" element={<Navigate to="/student/dashboard" replace />} />

        <Route path="/teacher" element={<TeacherGuard />}>
          <Route index element={<Navigate to="dashboard" replace />} />
          <Route path="dashboard" element={<TeacherDashboard />} />
          <Route path="tests" element={<TeacherTestsPage />} />
          <Route element={<TestCreationLayout />}>
            <Route path="tests/create" element={<CreateTestDetailsPage />} />
            <Route path="tests/create/questions" element={<CreateTestQuestionsPage />} />
            <Route path="tests/create/preview" element={<CreateTestPreviewPage />} />
          </Route>
          <Route path="tests/:testId/created" element={<TestCreatedSuccessPage />} />
          <Route path="tests/:testId" element={<TeacherTestDetailsPage />} />
        </Route>

        <Route
          path="/admin/*"
          element={
            <ProtectedRoute roles={['admin']}>
              <AdminDashboard />
            </ProtectedRoute>
          }
        />

        <Route path={ROUTES.UNAUTHORIZED} element={<UnauthorizedPage />} />
        <Route path={ROUTES.NOT_FOUND} element={<NotFoundPage />} />
        <Route path="*" element={<Navigate to={ROUTES.NOT_FOUND} replace />} />
      </Routes>
    </Suspense>
  )
}
