"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Scale, User } from "lucide-react";
import { SignInButton, SignUpButton, UserButton, useUser } from "@clerk/nextjs";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Inter, Poppins } from "next/font/google";
const poppins = Poppins({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-poppins",
});
export function Header() {
  const { isSignedIn, user } = useUser();
  if (!user) {
    return (
      <div
        className={`!${poppins.className} min-h-screen`}
        style={{ backgroundColor: "#EFEAE3" }}
      >
        <div className="flex items-center justify-center min-h-screen">
          <Card
            className="w-96"
            style={{ backgroundColor: "white", borderColor: "orangered" }}
          >
            <CardHeader>
              <CardTitle className="text-center" style={{ color: "orangered" }}>
                Authentication Required
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-center text-muted-foreground">
                Please sign in to access your dashboard.
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }
  return (
    <header className="sticky top-0 z-50 legal-bg-primary backdrop-blur-sm border-b border-legal-border transition-colors duration-300  w-full bg-cream-100/95  supports-[backdrop-filter]:bg-cream-100/80  border-stone-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center space-x-3 group">
            <span className="text-xl  font-bold text-brown-900 tracking-tight">
              OPAL
            </span>
          </Link>

          {/* Navigation */}
          <div className="flex items-center space-x-4">
            {isSignedIn ? (
              <>

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
