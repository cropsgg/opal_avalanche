'use client';

import Link from 'next/link';
import { Scale } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

export function Footer() {
  return (
    <footer className="bg-white border-t border-stone-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Newsletter Section */}
        <div className="mb-12">
          <div className="max-w-md">
            <h3 className="text-xl font-semibold text-brown-900 mb-2">
              Subscribe to the Opal Newsletter
            </h3>
            <p className="text-sage-600 text-sm mb-4">
              Latest news, musings, announcements and updates direct to your inbox.
            </p>
            <div className="flex gap-2">
              <Input
                type="email"
                placeholder="Enter your email"
                className="flex-1"
              />
              <Button className="bg-brown-700 hover:bg-brown-600 text-white">
                Subscribe
              </Button>
            </div>
          </div>
        </div>

        {/* Main Footer Content */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-8">
          {/* Products */}
          <div>
            <h4 className="font-medium text-brown-900 mb-4">Products</h4>
            <ul className="space-y-3">
              <li>
                <Link href="#" className="text-sage-600 hover:text-brown-700 text-sm transition-colors">
                  Research Assistant
                </Link>
              </li>
              <li>
                <Link href="#" className="text-sage-600 hover:text-brown-700 text-sm transition-colors">
                  Document Analysis
                </Link>
              </li>
              <li>
                <Link href="#" className="text-sage-600 hover:text-brown-700 text-sm transition-colors">
                  Case Management
                </Link>
              </li>
            </ul>
          </div>

          {/* Company */}
          <div>
            <h4 className="font-medium text-brown-900 mb-4">Company</h4>
            <ul className="space-y-3">
              <li>
                <Link href="#" className="text-sage-600 hover:text-brown-700 text-sm transition-colors">
                  About
                </Link>
              </li>
              <li>
                <Link href="#" className="text-sage-600 hover:text-brown-700 text-sm transition-colors">
                  Terms
                </Link>
              </li>
              <li>
                <Link href="#" className="text-sage-600 hover:text-brown-700 text-sm transition-colors">
                  Privacy
                </Link>
              </li>
            </ul>
          </div>

          {/* Resources */}
          <div>
            <h4 className="font-medium text-brown-900 mb-4">Resources</h4>
            <ul className="space-y-3">
              <li>
                <Link href="#" className="text-sage-600 hover:text-brown-700 text-sm transition-colors">
                  Support
                </Link>
              </li>
              <li>
                <Link href="#" className="text-sage-600 hover:text-brown-700 text-sm transition-colors">
                  Documentation
                </Link>
              </li>
              <li>
                <Link href="#" className="text-sage-600 hover:text-brown-700 text-sm transition-colors">
                  API Reference
                </Link>
              </li>
            </ul>
          </div>

          {/* Social */}
          <div>
            <h4 className="font-medium text-brown-900 mb-4">Social</h4>
            <ul className="space-y-3">
              <li>
                <Link href="#" className="text-sage-600 hover:text-brown-700 text-sm transition-colors">
                  Twitter
                </Link>
              </li>
              <li>
                <Link href="#" className="text-sage-600 hover:text-brown-700 text-sm transition-colors">
                  LinkedIn
                </Link>
              </li>
              <li>
                <Link href="#" className="text-sage-600 hover:text-brown-700 text-sm transition-colors">
                  GitHub
                </Link>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Section */}
        <div className="pt-8 border-t border-stone-200 flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-md bg-brown-700 text-cream-100">
              <Scale className="h-4 w-4" />
            </div>
            <span className="text-lg  font-bold text-brown-900 tracking-tight">
              OPAL
            </span>
          </div>

          <div className="text-sage-600 text-sm">
            © {new Date().getFullYear()} OPAL Legal Research. All rights reserved.
          </div>
        </div>
      </div>
    </footer>
  );
}
