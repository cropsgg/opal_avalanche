import './globals.css';
import type { Metadata } from 'next';
import { ClerkProvider } from '@clerk/nextjs';
import { Baskervville, Montserrat } from "next/font/google";
import "./globals.css";

const baskervville = Baskervville({
  subsets: ["latin"],
  weight: ["400"],
  style: ["italic", "normal"],
  variable: "--font-baskervville",
});
const montserrat = Montserrat({
  subsets: ["latin"],
  weight: ["400"],
  style: ["italic", "normal"],
  variable: "--font-montserrat",
});
export const metadata: Metadata = {
  title: 'OPAL - AI Legal Research Assistant',
  description: 'Advanced legal research and document analysis powered by AI',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ClerkProvider>
      <html lang="en">
        <body className="antialiased">
          {children}
        </body>
      </html>
    </ClerkProvider>
  );
}
