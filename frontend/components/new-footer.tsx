
"use client";

import { ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import type { FormEvent } from "react";

export function SiteFooter() {
  const onSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    // TODO: hook up to newsletter backend/provider
  };

  return (
    <footer className="relative overflow-hidden border-t border-stone-200 bg-cream-50">
      {/* Background oversized word */}
      <span
        aria-hidden="true"
        className="pointer-events-none select-none absolute left-1/2 top-1/2 -z-10 -translate-x-1/2 -translate-y-[58%] text-[52vw] leading-none tracking-[-0.06em] text-brown-900/10 md:text-[46vw] lg:text-[40vw]"
        style={{
          fontFamily:
            "ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial",
        }}
      >
        Opal
      </span>

      <div className="mx-auto max-w-7xl px-4 py-12 md:py-16">
        {/* Upper subtle divider like the reference */}
        <div className="h-px w-full bg-stone-200" />

        <div className="mt-10 grid gap-12 lg:grid-cols-12">
          {/* Newsletter block */}
          <div className="lg:col-span-6">
            <h3 className="font-merriweather text-xl font-semibold tracking-[-0.01em] text-brown-900">
              Subscribe to the
              <br />
              OPAL Newsletter
            </h3>
            <p className="mt-4 max-w-md text-sm text-brown-700">
              Latest news, musings, announcements
              <br />
              and updates direct to your inbox.
            </p>

            <form onSubmit={onSubmit} className="mt-6 max-w-md">
              <div className="flex items-center">
                <label htmlFor="newsletter-email" className="sr-only">
                  Email address
                </label>
                <Input
                  id="newsletter-email"
                  type="email"
                  required
                  placeholder="you@company.com"
                  className="h-12 rounded-l-full border-stone-200 bg-white text-brown-900 placeholder:text-brown-700/60"
                />
                <Button
                  type="submit"
                  aria-label="Subscribe"
                  className="h-12 rounded-r-full bg-brown-900 px-4 text-cream-100 hover:bg-brown-900/90"
                >
                  <ArrowRight className="h-5 w-5" />
                </Button>
              </div>
            </form>
          </div>

          {/* Link columns */}
          <div className="lg:col-span-6">
            <div className="grid grid-cols-2 gap-10 sm:grid-cols-4">
              <div>
                <div className="text-xs font-semibold uppercase tracking-wide text-brown-700/80">
                  Products
                </div>
                <ul className="mt-4 space-y-3 text-sm text-brown-900">
                  <li>
                    <a className="hover:opacity-80" href="#">
                      Tadpole
                    </a>
                  </li>
                  <li>
                    <a className="hover:opacity-80" href="#">
                      Opal C1
                    </a>
                  </li>
                  <li>
                    <a className="hover:opacity-80" href="#">
                      Composer
                    </a>
                  </li>
                </ul>
              </div>

              <div>
                <div className="text-xs font-semibold uppercase tracking-wide text-brown-700/80">
                  Company
                </div>
                <ul className="mt-4 space-y-3 text-sm text-brown-900">
                  <li>
                    <a className="hover:opacity-80" href="#">
                      About
                    </a>
                  </li>
                  <li>
                    <a className="hover:opacity-80" href="#">
                      Terms
                    </a>
                  </li>
                  <li>
                    <a className="hover:opacity-80" href="#">
                      Privacy
                    </a>
                  </li>
                </ul>
              </div>

              <div>
                <div className="text-xs font-semibold uppercase tracking-wide text-brown-700/80">
                  Resources
                </div>
                <ul className="mt-4 space-y-3 text-sm text-brown-900">
                  <li>
                    <a className="hover:opacity-80" href="#">
                      Support
                    </a>
                  </li>
                  <li>
                    <a className="hover:opacity-80" href="#">
                      Media Kit
                    </a>
                  </li>
                  <li>
                    <a className="hover:opacity-80" href="#">
                      Downloads
                    </a>
                  </li>
                  <li>
                    <a className="hover:opacity-80" href="#">
                      Newsletter
                    </a>
                  </li>
                </ul>
              </div>

              <div>
                <div className="text-xs font-semibold uppercase tracking-wide text-brown-700/80">
                  Social
                </div>
                <ul className="mt-4 space-y-3 text-sm text-brown-900">
                  <li>
                    <a className="hover:opacity-80" href="#">
                      Instagram
                    </a>
                  </li>
                  <li>
                    <a className="hover:opacity-80" href="#">
                      Twitter
                    </a>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom divider matching the ref spacing */}
        <div className="mt-12 h-px w-full bg-stone-200" />
        <div className="mt-6 text-xs text-brown-700/70">
          © {new Date().getFullYear()} OPAL. Guidance only. Not legal advice.
        </div>
      </div>
    </footer>
  );
}
