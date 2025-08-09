import { SignUp } from '@clerk/nextjs';

export default function SignUpPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-cream-50">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-sage-800 mb-2">Join OPAL</h1>
          <p className="text-sage-600">Create your account to get started</p>
        </div>
        <SignUp
          appearance={{
            elements: {
              formButtonPrimary: 'bg-sage-600 hover:bg-sage-700 text-white',
              card: 'bg-white shadow-lg',
              headerTitle: 'hidden',
              headerSubtitle: 'hidden',
            }
          }}
        />
      </div>
    </div>
  );
}
