'use client'

import { useState } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Lock, User, Eye, EyeOff } from 'lucide-react'

export default function LoginForm() {
  const { login, isLoading } = useAuth()
  const [formData, setFormData] = useState({
    userId: '',
    password: ''
  })
  const [error, setError] = useState('')
  const [showPassword, setShowPassword] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (!formData.userId.trim() || !formData.password.trim()) {
      setError('Please enter both User ID and Password')
      return
    }

    const success = await login(formData.userId, formData.password)
    if (!success) {
      setError('Invalid User ID or Password. Please try again.')
    }
  }

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    if (error) setError('') // Clear error when user starts typing
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-warm p-4">
      <Card className="w-full max-w-md bg-white/90 backdrop-blur-sm border-brown-200 shadow-elegant">
        <CardHeader className="text-center space-y-4">
          <div className="flex items-center justify-center">
            <div className="flex items-center justify-center w-16 h-16 bg-gradient-to-r from-brown-700 to-gold-500 rounded-2xl shadow-elegant">
              <Lock className="h-8 w-8 text-cream-100" />
            </div>
          </div>
          <div>
            <CardTitle className="text-2xl font-display font-bold text-brown-900">
              OPAL Server Access
            </CardTitle>
            <CardDescription className="text-brown-600 mt-2">
              Please sign in to access the blockchain and vector operations dashboard
            </CardDescription>
          </div>
        </CardHeader>

        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            {error && (
              <Alert className="border-red-200 bg-red-50">
                <AlertDescription className="text-red-700">
                  {error}
                </AlertDescription>
              </Alert>
            )}

            <div className="space-y-4">
              <div className="space-y-2">
                <label htmlFor="userId" className="text-sm font-medium text-brown-700">
                  User ID
                </label>
                <div className="relative">
                  <Input
                    id="userId"
                    type="text"
                    placeholder="Enter your User ID"
                    value={formData.userId}
                    onChange={(e) => handleInputChange('userId', e.target.value)}
                    className="pl-10 border-brown-300 focus:border-brown-500 focus:ring-brown-500"
                    disabled={isLoading}
                  />
                  <User className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-brown-400" />
                </div>
              </div>

              <div className="space-y-2">
                <label htmlFor="password" className="text-sm font-medium text-brown-700">
                  Password
                </label>
                <div className="relative">
                  <Input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    placeholder="Enter your Password"
                    value={formData.password}
                    onChange={(e) => handleInputChange('password', e.target.value)}
                    className="pl-10 pr-10 border-brown-300 focus:border-brown-500 focus:ring-brown-500"
                    disabled={isLoading}
                  />
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-brown-400" />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-brown-400 hover:text-brown-600"
                    disabled={isLoading}
                  >
                    {showPassword ? (
                      <EyeOff className="h-4 w-4" />
                    ) : (
                      <Eye className="h-4 w-4" />
                    )}
                  </button>
                </div>
              </div>
            </div>

            <Button
              type="submit"
              disabled={isLoading}
              className="w-full bg-brown-700 hover:bg-brown-600 text-white font-medium py-2.5 transition-colors duration-300"
            >
              {isLoading ? (
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Signing In...</span>
                </div>
              ) : (
                'Sign In'
              )}
            </Button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-xs text-brown-500">
              Secure access to OPAL blockchain and vector database operations
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
