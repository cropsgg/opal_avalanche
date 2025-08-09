'use client';

import { SignUp } from '@clerk/nextjs';
import { Loader2 } from 'lucide-react';
import { Suspense } from 'react';

function SignUpForm() {
  return (
    <SignUp
      appearance={{
        elements: {
          formButtonPrimary: 'bg-brown-700 hover:bg-brown-600 text-white',
          card: 'bg-white shadow-lg border border-stone-200',
          headerTitle: 'hidden',
          headerSubtitle: 'hidden',
          socialButtonsBlockButton: 'border-stone-300 hover:bg-stone-50',
          formFieldInput: 'border-stone-300 focus:border-brown-500',
          footerActionLink: 'text-brown-700 hover:text-brown-500',
        },
        variables: {
          colorPrimary: '#8B4513',
          colorText: '#1C1917',
          colorTextSecondary: '#78716C',
          colorBackground: '#FFFBEB',
          colorInputBackground: '#FFFFFF',
          colorInputText: '#1C1917',
          borderRadius: '0.5rem',
        },
      }}
      redirectUrl="/dashboard"
    />
  );
}

export default function SignUpPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-cream-50">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-brown-900 mb-2">Join OPAL</h1>
          <p className="text-brown-600">Create your account to get started</p>
        </div>
        <Suspense 
          fallback={
            <div className="flex items-center justify-center p-8">
              <Loader2 className="h-8 w-8 animate-spin text-brown-700" />
            </div>
          }
        >
          <SignUpForm />
        </Suspense>
      </div>
    </div>
  );
}
