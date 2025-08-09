import './globals.css';
import type { Metadata } from 'next';
import { ClerkProvider } from '@clerk/nextjs';
import { Inter } from 'next/font/google';
import { Toaster } from '@/components/ui/toaster';
import ErrorBoundary from '@/components/ErrorBoundary';

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
});

export const metadata: Metadata = {
  title: 'OPAL - AI Legal Research Assistant',
  description: 'Advanced legal research and document analysis powered by AI for Indian lawyers',
  keywords: ['legal research', 'AI', 'Indian law', 'precedent analysis', 'legal tech'],
  authors: [{ name: 'OPAL Team' }],
  creator: 'OPAL',
  metadataBase: new URL('https://opal.legal'),
  openGraph: {
    title: 'OPAL - AI Legal Research Assistant',
    description: 'Advanced legal research and document analysis powered by AI for Indian lawyers',
    type: 'website',
    locale: 'en_IN',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ClerkProvider
      appearance={{
        elements: {
          formButtonPrimary: 'bg-brown-700 hover:bg-brown-600 text-cream-100',
          card: 'shadow-lg border border-stone-200',
          headerTitle: 'text-brown-900 font-display',
          headerSubtitle: 'text-brown-500',
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
    >
      <html lang="en" className={inter.variable}>
        <body className="min-h-screen bg-cream-50 font-sans antialiased">
          <ErrorBoundary>
            <div className="relative flex min-h-screen flex-col">
              <main className="flex-1">
                {children}
              </main>
            </div>
            <Toaster />
          </ErrorBoundary>
        </body>
      </html>
    </ClerkProvider>
  );
}
