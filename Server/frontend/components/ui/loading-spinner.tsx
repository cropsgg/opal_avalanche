'use client'

import { cn } from '@/lib/utils'

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl'
  className?: string
  color?: 'primary' | 'secondary' | 'gold' | 'white'
}

const sizeClasses = {
  sm: 'w-4 h-4',
  md: 'w-6 h-6', 
  lg: 'w-8 h-8',
  xl: 'w-12 h-12'
}

const colorClasses = {
  primary: 'text-brown-700',
  secondary: 'text-brown-500',
  gold: 'text-gold-500',
  white: 'text-white'
}

export function LoadingSpinner({ 
  size = 'md', 
  className,
  color = 'primary' 
}: LoadingSpinnerProps) {
  return (
    <div 
      className={cn(
        'animate-spin rounded-full border-2 border-current border-t-transparent',
        sizeClasses[size],
        colorClasses[color],
        className
      )}
      role="status"
      aria-label="Loading"
    >
      <span className="sr-only">Loading...</span>
    </div>
  )
}

export function LoadingDots({ className }: { className?: string }) {
  return (
    <div className={cn('flex space-x-1', className)}>
      <div className="w-2 h-2 bg-current rounded-full animate-pulse"></div>
      <div className="w-2 h-2 bg-current rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
      <div className="w-2 h-2 bg-current rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
    </div>
  )
}

export function LoadingCard() {
  return (
    <div className="bg-white/80 backdrop-blur-sm border border-brown-200 rounded-2xl p-6 shadow-soft animate-fadeIn">
      <div className="animate-shimmer bg-gradient-to-r from-brown-100 via-brown-50 to-brown-100 bg-[length:400px_100%] h-4 rounded mb-4"></div>
      <div className="space-y-3">
        <div className="animate-shimmer bg-gradient-to-r from-brown-100 via-brown-50 to-brown-100 bg-[length:400px_100%] h-3 rounded w-3/4"></div>
        <div className="animate-shimmer bg-gradient-to-r from-brown-100 via-brown-50 to-brown-100 bg-[length:400px_100%] h-3 rounded w-1/2"></div>
      </div>
    </div>
  )
}

export function LoadingPage() {
  return (
    <div className="min-h-screen bg-gradient-warm flex items-center justify-center">
      <div className="text-center space-y-8">
        <div className="relative">
          <div className="w-24 h-24 bg-gradient-to-r from-brown-700 to-gold-500 rounded-3xl flex items-center justify-center animate-float">
            <LoadingSpinner size="xl" color="white" />
          </div>
          <div className="absolute -inset-4 bg-gradient-to-r from-brown-700 to-gold-500 rounded-3xl opacity-20 animate-ping"></div>
        </div>
        <div className="space-y-2">
          <h2 className="text-2xl font-display font-bold text-brown-900">Loading OPAL Server</h2>
          <p className="text-brown-600">Initializing blockchain and vector operations...</p>
        </div>
        <LoadingDots className="text-brown-500 justify-center" />
      </div>
    </div>
  )
}
