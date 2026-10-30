import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { ROUTES } from '../../utils/constants'

function Icon({ name }) {
  const icons = {
    dashboard: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <rect x="3" y="3" width="7" height="7" /><rect x="14" y="3" width="7" height="7" />
        <rect x="14" y="14" width="7" height="7" /><rect x="3" y="14" width="7" height="7" />
      </svg>
    ),
    code: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <polyline points="16 18 22 12 16 6" /><polyline points="8 6 2 12 8 18" />
      </svg>
    ),
    records: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
        <polyline points="14 2 14 8 20 8" /><line x1="16" y1="13" x2="8" y2="13" />
        <line x1="16" y1="17" x2="8" y2="17" /><polyline points="10 9 9 9 8 9" />
      </svg>
    ),
    tests: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M9 11l3 3L22 4" />
        <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11" />
      </svg>
    ),
    create: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <line x1="12" y1="5" x2="12" y2="19" /><line x1="5" y1="12" x2="19" y2="12" />
      </svg>
    ),
    users: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
        <circle cx="9" cy="7" r="4" />
      </svg>
    ),
    alert: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
        <line x1="12" y1="9" x2="12" y2="13" /><line x1="12" y1="17" x2="12.01" y2="17" />
      </svg>
    ),
    help: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="12" r="10" />
        <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3" />
        <line x1="12" y1="17" x2="12.01" y2="17" />
      </svg>
    ),
    profile: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
        <circle cx="12" cy="7" r="4" />
      </svg>
    ),
  }
  return icons[name] || null
}

function NavItem({ to, icon, label }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        [
          'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150',
          isActive
            ? 'bg-[var(--color-primary)] text-white'
            : 'text-[var(--color-text-secondary)] hover:bg-[var(--color-surface-soft)] hover:text-[var(--color-text-primary)]',
        ].join(' ')
      }
    >
      <Icon name={icon} />
      <span>{label}</span>
    </NavLink>
  )
}

export default function NavRail() {
  const { user, logout, isStudent, isTeacher, isAdmin } = useAuth()
  const navigate = useNavigate()

  const handleLogout = async () => {
    await logout()
    navigate(ROUTES.LOGIN)
  }

  const profileRoute = isStudent
    ? ROUTES.STUDENT_PROFILE
    : isTeacher
    ? ROUTES.TEACHER_PROFILE
    : ROUTES.ADMIN_PROFILE

  return (
    <aside className="w-56 min-h-screen flex flex-col bg-[var(--color-surface)] border-r border-[var(--color-border)] p-4 shrink-0">
      {/* Brand */}
      <div className="flex items-center gap-2.5 px-2 mb-8 mt-2">
        <div className="w-9 h-9 rounded-xl bg-[var(--color-primary)] flex items-center justify-center shadow-sm">
          <span className="font-display font-extrabold text-[var(--color-mint)] text-base">P</span>
        </div>
        <div>
          <span className="font-display font-bold text-[var(--color-text-primary)] text-base tracking-tight block">
            Proxam AI
          </span>
          <span className="text-[10px] text-[var(--color-text-muted)] tracking-wider uppercase font-semibold">
            {user?.role || 'Portal'}
          </span>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex flex-col gap-1.5 flex-1">
        {isStudent && (
          <>
            <NavItem to={ROUTES.STUDENT_DASHBOARD} icon="dashboard" label="Dashboard" />
            <NavItem to={ROUTES.STUDENT_ENTER_CODE} icon="code" label="Enter Test Code" />
            <NavItem to={ROUTES.STUDENT_HISTORY} icon="records" label="My Records" />
            <NavItem to={ROUTES.HELP} icon="help" label="Help & Support" />
          </>
        )}

        {isTeacher && (
          <>
            <NavItem to={ROUTES.TEACHER_DASHBOARD} icon="dashboard" label="Dashboard" />
            <NavItem to={ROUTES.TEACHER_TESTS} icon="tests" label="My Tests" />
            <NavItem to={ROUTES.TEACHER_CREATE_DETAILS} icon="create" label="Create Test" />
            <NavItem to={ROUTES.HELP} icon="help" label="Help & Support" />
          </>
        )}

        {isAdmin && (
          <>
            <NavItem to={ROUTES.ADMIN_DASHBOARD} icon="dashboard" label="Overview" />
            <NavItem to={ROUTES.ADMIN_USERS} icon="users" label="Users" />
            <NavItem to={ROUTES.ADMIN_TESTS} icon="tests" label="Tests" />
            <NavItem to={ROUTES.ADMIN_PROCTORING} icon="alert" label="Proctoring Alerts" />
            <NavItem to={ROUTES.HELP} icon="help" label="Help" />
          </>
        )}
      </nav>

      {/* User and Logout */}
      <div className="pt-4 border-t border-[var(--color-border)] flex flex-col gap-1">
        <NavItem to={profileRoute} icon="profile" label="Profile" />
        <button
          onClick={handleLogout}
          className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-[var(--color-text-muted)] hover:bg-[var(--color-surface-soft)] hover:text-[var(--color-danger)] transition-all duration-150 w-full text-left"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
            <polyline points="16 17 21 12 16 7" />
            <line x1="21" y1="12" x2="9" y2="12" />
          </svg>
          <span>Log out</span>
        </button>

        {user && (
          <div className="px-3 py-2 mt-2 bg-[var(--color-surface-soft)] rounded-lg">
            <p className="text-xs font-semibold text-[var(--color-text-primary)] truncate">{user.full_name}</p>
            <p className="text-[11px] text-[var(--color-text-muted)] truncate">{user.email}</p>
          </div>
        )}
      </div>
    </aside>
  )
}
