import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../auth/useAuth'

interface Breadcrumb {
  label: string
  to?: string
}

interface AppLayoutProps {
  title: string
  breadcrumbs?: Breadcrumb[]
  children: React.ReactNode
}

export default function AppLayout({
  title,
  breadcrumbs,
  children,
}: AppLayoutProps) {
  const { logout } = useAuth()
  const location = useLocation()
  const [menuOpen, setMenuOpen] = useState(false)

  const isDashboard = location.pathname === '/dashboard'

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="mx-auto max-w-4xl px-4 py-3 sm:py-4">
          <div className="flex items-center justify-between">
            {/* Left: title area */}
            <div className="min-w-0 flex-1">
              {breadcrumbs && breadcrumbs.length > 0 && (
                <nav className="mb-1 flex flex-wrap items-center gap-x-1 text-sm text-gray-500">
                  {breadcrumbs.map((crumb, i) => (
                    <span key={i} className="flex items-center">
                      {i > 0 && <span className="mx-1">/</span>}
                      {crumb.to ? (
                        <Link
                          to={crumb.to}
                          className="hover:text-blue-600"
                        >
                          {crumb.label}
                        </Link>
                      ) : (
                        <span className="text-gray-900">{crumb.label}</span>
                      )}
                    </span>
                  ))}
                </nav>
              )}
              <h1 className="truncate text-xl font-bold text-gray-900 sm:text-2xl">
                {title}
              </h1>
            </div>

            {/* Right: desktop nav */}
            <div className="ml-4 hidden items-center gap-4 sm:flex">
              {!isDashboard && (
                <Link
                  to="/dashboard"
                  className="text-sm text-gray-500 hover:text-gray-700"
                >
                  Projects
                </Link>
              )}
              <button
                onClick={logout}
                className="text-sm text-gray-500 hover:text-gray-700"
              >
                Log out
              </button>
            </div>

            {/* Right: mobile hamburger */}
            <button
              type="button"
              onClick={() => setMenuOpen(!menuOpen)}
              className="ml-4 rounded-md p-2 text-gray-500 hover:bg-gray-100 hover:text-gray-700 sm:hidden"
              aria-label="Toggle menu"
            >
              {menuOpen ? (
                <svg
                  width="24"
                  height="24"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                >
                  <path d="M6 6l12 12M6 18L18 6" />
                </svg>
              ) : (
                <svg
                  width="24"
                  height="24"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                >
                  <path d="M3 6h18M3 12h18M3 18h18" />
                </svg>
              )}
            </button>
          </div>

          {/* Mobile menu dropdown */}
          {menuOpen && (
            <div className="mt-3 border-t border-gray-200 pt-3 sm:hidden">
              <div className="flex flex-col gap-2">
                {!isDashboard && (
                  <Link
                    to="/dashboard"
                    onClick={() => setMenuOpen(false)}
                    className="rounded-md px-3 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    Projects
                  </Link>
                )}
                <button
                  onClick={() => {
                    setMenuOpen(false)
                    logout()
                  }}
                  className="rounded-md px-3 py-2 text-left text-sm text-gray-700 hover:bg-gray-100"
                >
                  Log out
                </button>
              </div>
            </div>
          )}
        </div>
      </header>

      <main className="mx-auto max-w-4xl px-4 py-6 sm:py-8">{children}</main>
    </div>
  )
}
