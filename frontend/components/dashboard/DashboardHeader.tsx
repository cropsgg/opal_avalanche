'use client';

import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Scale, Plus, Search, Bell } from 'lucide-react';
import { UserButton } from '@clerk/nextjs';

export function DashboardHeader() {
  return (
    <header className="bg-cream-100 border-b border-stone-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link href="/dashboard" className="flex items-center space-x-3 group">
            <div className="p-2 rounded-md bg-brown-700 text-cream-100 group-hover:bg-brown-500 transition-colors">
              <Scale className="h-5 w-5" />
            </div>
            <span className="text-xl font-display font-bold text-brown-900 tracking-tight">
              OPAL
            </span>
          </Link>

          {/* Search */}
          <div className="hidden md:flex items-center flex-1 max-w-md mx-8">
            <div className="relative w-full">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-brown-500 h-4 w-4" />
              <input
                type="text"
                placeholder="Search matters, cases..."
                className="w-full pl-10 pr-4 py-2 border border-stone-200 rounded-md bg-white text-brown-900 placeholder-brown-500 focus:outline-none focus:ring-2 focus:ring-brown-700 focus:border-transparent"
              />
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center space-x-4">
            <Link href="/matters/new">
              <Button className="bg-brown-700 hover:bg-brown-500 text-cream-100 border border-gold-500">
                <Plus className="h-4 w-4 mr-2" />
                New Matter
              </Button>
            </Link>
            <Button variant="ghost" size="icon" className="text-brown-500 hover:text-brown-700">
              <Bell className="h-4 w-4" />
            </Button>
            <UserButton afterSignOutUrl="/" />
          </div>
        </div>
      </div>
    </header>
  );
}