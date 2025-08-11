'use client'

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { authApi, setAuthToken } from '@/lib/api'

interface User {
  user_id: string
  authenticated: boolean
  session_created: string
}

interface AuthContextType {
  user: User | null
  token: string | null
  isLoading: boolean
  login: (userId: string, password: string) => Promise<boolean>
  logout: () => void
  isAuthenticated: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

interface AuthProviderProps {
  children: ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Check for existing token on mount
    const savedToken = localStorage.getItem('opal_auth_token')
    if (savedToken) {
      setToken(savedToken)
      validateToken(savedToken)
    } else {
      setIsLoading(false)
    }
  }, [])

  const validateToken = async (authToken: string) => {
    try {
      setAuthToken(authToken) // Set token for API requests
      const userInfo = await authApi.getCurrentUser(authToken)
      setUser(userInfo)
      setToken(authToken)
    } catch (error) {
      console.error('Token validation failed:', error)
      localStorage.removeItem('opal_auth_token')
      setAuthToken(null) // Clear token from API requests
      setToken(null)
      setUser(null)
    } finally {
      setIsLoading(false)
    }
  }

  const login = async (userId: string, password: string): Promise<boolean> => {
    setIsLoading(true)
    try {
      const response = await authApi.login(userId, password)
      
      setToken(response.access_token)
      localStorage.setItem('opal_auth_token', response.access_token)
      setAuthToken(response.access_token) // Set token for API requests
      
      // Get user info
      const userInfo = await authApi.getCurrentUser(response.access_token)
      setUser(userInfo)
      
      return true
    } catch (error) {
      console.error('Login failed:', error)
      return false
    } finally {
      setIsLoading(false)
    }
  }

  const logout = async () => {
    try {
      if (token) {
        await authApi.logout(token)
      }
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      localStorage.removeItem('opal_auth_token')
      setAuthToken(null) // Clear token from API requests
      setToken(null)
      setUser(null)
    }
  }

  const value: AuthContextType = {
    user,
    token,
    isLoading,
    login,
    logout,
    isAuthenticated: !!user && !!token
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
