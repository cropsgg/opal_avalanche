'use client';

import { Button } from '@/components/ui/button';
import { ArrowRight, FileText, Bot, Shield } from 'lucide-react';
import { SignUpButton } from '@clerk/nextjs';

export function LandingHero() {
  return (
    <section className="relative py-20 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="text-center">
          <h1 className="text-5xl md:text-6xl font-display font-bold text-brown-900 tracking-tight mb-6">
            AI-Powered Legal
            <span className="block text-gold-500">Research Assistant</span>
          </h1>
          
          <p className="text-xl text-brown-500 mb-8 max-w-3xl mx-auto leading-relaxed">
            Transform your legal research with advanced AI that analyzes documents, 
            finds precedents, and provides verified citations with blockchain-backed provenance.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
            <SignUpButton mode="modal">
              <Button size="lg" className="bg-brown-700 hover:bg-brown-500 text-cream-100 border border-gold-500 px-8 py-3">
                Try Demo
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </SignUpButton>
            <Button size="lg" variant="outline" className="border-brown-700 text-brown-700 hover:bg-brown-50 px-8 py-3">
              Request Pilot
            </Button>
          </div>

          {/* Trust indicators */}
          <div className="flex flex-wrap justify-center gap-8 text-brown-500 text-sm">
            <div className="flex items-center gap-2">
              <FileText className="h-4 w-4" />
              <span>No Fake Citations</span>
            </div>
            <div className="flex items-center gap-2">
              <Bot className="h-4 w-4" />
              <span>AI-Verified Research</span>
            </div>
            <div className="flex items-center gap-2">
              <Shield className="h-4 w-4" />
              <span>Blockchain Notarized</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}