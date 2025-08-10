'use client';

import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Scale, Plus, Search, Bell } from 'lucide-react';
import { UserButton } from '@clerk/nextjs';

export function DashboardHeader() {
  return (
    <header style={{ backgroundColor: 'white', borderBottom: '1px solid #D1D5DB' }}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link href="/dashboard" className="flex items-center space-x-3 group">
            <div className="p-2 rounded-md group-hover:opacity-80 transition-opacity" style={{ backgroundColor: 'orangered', color: 'white' }}>
              <Scale className="h-5 w-5" />
            </div>
            <span className="text-xl font-display font-bold tracking-tight" style={{ color: 'orangered' }}>
              OPAL
            </span>
          </Link>

          {/* Search */}
          <div className="hidden md:flex items-center flex-1 max-w-md mx-8">
            <div className="relative w-full">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4" style={{ color: '#6B7280' }} />
              <input
                type="text"
                placeholder="Search matters, cases..."
                className="w-full pl-10 pr-4 py-2 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
                style={{ 
                  backgroundColor: '#F9FAFB',
                  border: '1px solid #D1D5DB',
                  color: '#111827'
                }}
              />
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center space-x-4">
            <Link href="/matters/new">
              <Button 
                className="border transition-colors hover:opacity-90"
                style={{ 
                  backgroundColor: 'orangered', 
                  color: 'white',
                  borderColor: 'orangered'
                }}
              >
                <Plus className="h-4 w-4 mr-2" />
                New Matter
              </Button>
            </Link>
            <Button variant="ghost" size="icon" className="hover:bg-gray-100" style={{ color: '#6B7280' }}>
              <Bell className="h-4 w-4" />
            </Button>
            <UserButton afterSignOutUrl="/" />
          </div>
        </div>
      </div>
    </header>
  );
}