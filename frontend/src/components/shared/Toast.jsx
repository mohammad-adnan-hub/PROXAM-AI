import { createContext, useCallback, useContext, useState } from 'react'

const ToastContext = createContext(null)

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([])

  const addToast = useCallback(({ message, type = 'info', duration = 4000 }) => {
    const id = Date.now() + Math.random()
    setToasts((prev) => [...prev, { id, message, type }])
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id))
    }, duration)
  }, [])

  const removeToast = useCallback((id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id))
  }, [])

  const toast = {
    success: (message) => addToast({ message, type: 'success' }),
    error: (message) => addToast({ message, type: 'error' }),
    warning: (message) => addToast({ message, type: 'warning' }),
    info: (message) => addToast({ message, type: 'info' }),
  }

  const typeStyles = {
    success: 'bg-[var(--color-success)] text-[var(--color-text-primary)]',
    error: 'bg-[var(--color-danger)] text-[var(--color-text-primary)]',
    warning: 'bg-[var(--color-warning)] text-[var(--color-text-primary)]',
    info: 'bg-[var(--color-info)] text-[var(--color-text-primary)]',
  }

  return (
    <ToastContext.Provider value={toast}>
      {children}
      <div className="fixed bottom-6 right-6 z-[100] flex flex-col gap-2 items-end pointer-events-none">
        {toasts.map((t) => (
          <div
            key={t.id}
            className={`pointer-events-auto flex items-center gap-3 px-4 py-3 rounded-lg shadow-card-md text-sm font-medium max-w-sm ${typeStyles[t.type]}`}
          >
            <span className="flex-1">{t.message}</span>
            <button
              onClick={() => removeToast(t.id)}
              className="opacity-60 hover:opacity-100 transition-opacity ml-2"
              aria-label="Dismiss"
            >
              ✕
            </button>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  )
}

export function useToast() {
  const ctx = useContext(ToastContext)
  if (!ctx) throw new Error('useToast must be used within ToastProvider')
  return ctx
}
