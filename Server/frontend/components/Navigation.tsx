'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'
import { useAuth } from '@/contexts/AuthContext'
import { Button } from '@/components/ui/button'
import { 
  Home, 
  Blocks, 
  Search, 
  Activity, 
  Database,
  Zap,
  ChevronDown,
  ExternalLink,
  LogOut,
  User
} from 'lucide-react'

const navigation = [
  { name: 'Dashboard', href: '/', icon: Home },
  { name: 'Blockchain', href: '/blockchain', icon: Blocks },
  { name: 'Search', href: '/search', icon: Search },
  { name: 'Knowledge Graph', href: '/knowledge-graph', icon: Database },
  { name: 'Status', href: '/status', icon: Activity },
]

export default function Navigation() {
  const pathname = usePathname()
  const { user, logout } = useAuth()

  return (
    <nav className="bg-white/95 backdrop-blur-lg border-b border-brown-200 shadow-soft sticky top-0 z-50">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-20">
          {/* Logo */}
          <Link href="/" className="flex items-center space-x-3 group">
            <div className="relative">
              <div className="flex items-center justify-center w-12 h-12 bg-gradient-to-br from-brown-700 to-gold-500 rounded-xl shadow-elegant group-hover:shadow-lg transition-all duration-300 group-hover:scale-105">
                <Zap className="h-6 w-6 text-cream-100" />
              </div>
              <div className="absolute -top-1 -right-1 w-4 h-4 bg-green-500 rounded-full flex items-center justify-center">
                <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
              </div>
            </div>
            <div className="hidden sm:block">
              <div className="font-display font-bold text-xl text-brown-900 group-hover:text-brown-700 transition-colors">
                OPAL Server
              </div>
              <div className="text-sm text-brown-600 font-medium">
                Blockchain & Vector Operations
              </div>
            </div>
          </Link>

          {/* Navigation Links */}
          <div className="hidden lg:flex items-center space-x-2">
            {navigation.map((item) => {
              const isActive = pathname === item.href || (item.href !== '/' && pathname.startsWith(item.href))
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={cn(
                    'flex items-center space-x-2 px-4 py-3 rounded-xl font-medium transition-all duration-300 relative group',
                    isActive
                      ? 'bg-gradient-to-r from-brown-700 to-gold-500 text-white shadow-elegant'
                      : 'text-brown-600 hover:text-brown-900 hover:bg-brown-50'
                  )}
                >
                  <item.icon className={cn(
                    'h-5 w-5 transition-transform duration-300',
                    isActive ? 'text-white' : 'text-brown-500',
                    'group-hover:scale-110'
                  )} />
                  <span className="text-sm">{item.name}</span>
                  {isActive && (
                    <div className="absolute inset-0 bg-gradient-to-r from-brown-700 to-gold-500 rounded-xl animate-glow -z-10"></div>
                  )}
                </Link>
              )
            })}
          </div>

          {/* Right Side Actions */}
          <div className="flex items-center space-x-4">
            {/* API Docs Link */}
            <Link 
              href="/docs" 
              target="_blank"
              className="hidden md:flex items-center space-x-2 px-3 py-2 text-brown-600 hover:text-brown-900 transition-colors group"
            >
              <span className="text-sm font-medium">API Docs</span>
              <ExternalLink className="h-4 w-4 group-hover:scale-110 transition-transform" />
            </Link>

            {/* User Info */}
            {user && (
              <div className="hidden md:flex items-center space-x-2 px-3 py-2 bg-blue-50 rounded-lg border border-blue-200">
                <User className="h-4 w-4 text-blue-600" />
                <span className="text-sm font-medium text-blue-700">{user.user_id}</span>
              </div>
            )}

            {/* Status Indicator */}
            <div className="flex items-center space-x-2 px-3 py-2 bg-green-50 rounded-lg border border-green-200">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse relative">
                  <div className="absolute inset-0 bg-green-500 rounded-full animate-ping opacity-75"></div>
                </div>
                <span className="text-sm font-medium text-green-700 hidden sm:block">
                  System Online
                </span>
              </div>
            </div>

            {/* Logout Button */}
            <Button
              onClick={logout}
              variant="outline"
              size="sm"
              className="hidden md:flex items-center space-x-2 border-brown-300 text-brown-700 hover:bg-brown-50"
            >
              <LogOut className="h-4 w-4" />
              <span>Logout</span>
            </Button>
          </div>
        </div>

        {/* Mobile Navigation */}
        <div className="lg:hidden border-t border-brown-200">
          <div className="grid grid-cols-5 gap-1 py-3">
            {navigation.map((item) => {
              const isActive = pathname === item.href || (item.href !== '/' && pathname.startsWith(item.href))
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={cn(
                    'flex flex-col items-center space-y-1 px-2 py-3 rounded-lg text-xs font-medium transition-all duration-300',
                    isActive
                      ? 'bg-gradient-to-b from-brown-700 to-gold-500 text-white shadow-soft'
                      : 'text-brown-600 hover:text-brown-900 hover:bg-brown-50'
                  )}
                >
                  <item.icon className={cn(
                    'h-5 w-5 transition-transform duration-300',
                    isActive ? 'text-white scale-110' : 'text-brown-500'
                  )} />
                  <span className={cn(
                    'text-center leading-tight',
                    item.name.length > 8 ? 'text-[10px]' : 'text-xs'
                  )}>
                    {item.name}
                  </span>
                </Link>
              )
            })}
          </div>
        </div>
      </div>
    </nav>
  )
}
