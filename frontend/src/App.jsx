import { AuthProvider } from './context/AuthContext'
import { ToastProvider } from './components/shared/Toast'
import AppRoutes from './routes'

export default function App() {
  return (
    <AuthProvider>
      <ToastProvider>
        <AppRoutes />
      </ToastProvider>
    </AuthProvider>
  )
}
