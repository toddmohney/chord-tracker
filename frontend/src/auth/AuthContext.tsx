import { useState, useEffect, useCallback, type ReactNode } from 'react'
import { setAccessToken } from '../api/client'
import { AuthContext } from './authTypes'
import type { User } from './authTypes'

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  const fetchUser = useCallback(async (token: string): Promise<User | null> => {
    const response = await fetch('/api/auth/me', {
      headers: { Authorization: `Bearer ${token}` },
    })
    if (!response.ok) return null
    return response.json()
  }, [])

  useEffect(() => {
    async function tryRestore() {
      const refreshToken = localStorage.getItem('refreshToken')
      if (!refreshToken) {
        setLoading(false)
        return
      }

      const response = await fetch('/api/auth/refresh', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken }),
      })

      if (!response.ok) {
        localStorage.removeItem('refreshToken')
        setLoading(false)
        return
      }

      const data = await response.json()
      setAccessToken(data.access_token)
      const restored = await fetchUser(data.access_token)
      setUser(restored)
      setLoading(false)
    }

    tryRestore()
  }, [fetchUser])

  const login = useCallback(async (email: string, password: string) => {
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    })

    if (!response.ok) {
      const data = await response.json()
      throw new Error(data.detail || 'Login failed')
    }

    const data = await response.json()
    setAccessToken(data.access_token)
    localStorage.setItem('refreshToken', data.refresh_token)

    const loggedIn = await fetchUser(data.access_token)
    setUser(loggedIn)
  }, [fetchUser])

  const signup = useCallback(async (email: string, password: string) => {
    const registerResponse = await fetch('/api/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    })

    if (!registerResponse.ok) {
      const data = await registerResponse.json()
      throw new Error(data.detail || 'Registration failed')
    }

    await login(email, password)
  }, [login])

  const logout = useCallback(() => {
    setAccessToken(null)
    localStorage.removeItem('refreshToken')
    setUser(null)
  }, [])

  return (
    <AuthContext.Provider value={{ user, loading, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  )
}
