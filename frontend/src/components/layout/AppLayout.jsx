import NavRail from './NavRail'

export default function AppLayout({ children }) {
  return (
    <div className="flex min-h-screen bg-[var(--color-background)]">
      <NavRail />
      <main className="flex-1 overflow-auto">
        <div className="max-w-5xl mx-auto px-8 py-8">{children}</div>
      </main>
    </div>
  )
}
