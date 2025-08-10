'use client';

import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { NetworkStatus } from '@/components/ui/network-status';
import { Scale, User } from 'lucide-react';
import { SignInButton, SignUpButton, UserButton, useUser } from '@clerk/nextjs';

export function Header() {
  const { isSignedIn } = useUser();

  return (
    <header className="sticky top-0 z-50 legal-bg-primary backdrop-blur-sm border-b border-legal-border transition-colors duration-300  w-full bg-cream-100/95  supports-[backdrop-filter]:bg-cream-100/80  border-stone-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center space-x-3 group">
            <div className="p-2 rounded-md bg-brown-700 text-cream-100 group-hover:bg-brown-500 transition-colors">
              <Scale className="h-5 w-5" />
            </div>
            <span className="text-xl font-display font-bold text-brown-900 tracking-tight">
              OPAL
            </span>
          </Link>

          {/* Navigation */}
          <div className="flex items-center space-x-4">
            {isSignedIn ? (
              <>
                <NetworkStatus />
                <Link href="/dashboard">
                  <Button
                    variant="ghost"
                    className="text-brown-700 hover:text-brown-900"
                  >
                    Dashboard
                  </Button>
                </Link>
                <UserButton afterSignOutUrl="/" />
              </>
            ) : (
              <>
                <SignInButton>
                  <Button
                    variant="ghost"
                    className="text-brown-700 hover:text-brown-900"
                  >
                    Sign In
                  </Button>
                </SignInButton>
                <SignUpButton>
                  <Button className="bg-brown-700 hover:bg-brown-500 text-cream-100 border border-gold-500">
                    Get Started
                  </Button>
                </SignUpButton>
              </>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
