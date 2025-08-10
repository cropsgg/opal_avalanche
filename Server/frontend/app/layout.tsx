import type { Metadata } from 'next'
import { Playfair_Display, Merriweather } from 'next/font/google'
import './globals.css'
import Navigation from '@/components/Navigation'

const playfair = Playfair_Display({ 
  subsets: ['latin'], 
  variable: '--font-playfair',
  display: 'swap'
})

const merriweather = Merriweather({ 
  subsets: ['latin'], 
  weight: ['300', '400', '700'],
  variable: '--font-merriweather',
  display: 'swap'
})

export const metadata: Metadata = {
  title: 'OPAL Server | Blockchain & Vector Database Operations',
  description: 'Advanced blockchain notarization and vector database operations for legal document integrity and discovery.',
  icons: {
    icon: '/favicon.ico',
  },
  openGraph: {
    title: 'OPAL Server',
    description: 'Blockchain and Vector Database Operations for Legal AI',
    type: 'website',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={`${playfair.variable} ${merriweather.variable}`}>
      <body className="min-h-screen bg-gradient-warm text-brown-900 font-body antialiased">
        <div className="min-h-screen">
          <Navigation />
          <main className="relative">
            {children}
          </main>
        </div>
        
        {/* Background decorative elements */}
        <div className="fixed inset-0 overflow-hidden pointer-events-none -z-10">
          <div className="absolute -top-4 -right-4 w-72 h-72 bg-gold-500 rounded-full mix-blend-multiply filter blur-xl opacity-10 animate-float"></div>
          <div className="absolute -bottom-8 -left-4 w-72 h-72 bg-brown-500 rounded-full mix-blend-multiply filter blur-xl opacity-10 animate-float" style={{animationDelay: '2s'}}></div>
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-olive-400 rounded-full mix-blend-multiply filter blur-xl opacity-5 animate-float" style={{animationDelay: '4s'}}></div>
        </div>
      </body>
    </html>
  )
}
