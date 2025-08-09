import { SignIn } from '@clerk/nextjs';

export default function SignInPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-cream-50">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-sage-800 mb-2">Welcome Back</h1>
          <p className="text-sage-600">Sign in to your OPAL account</p>
        </div>
        <SignIn
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
