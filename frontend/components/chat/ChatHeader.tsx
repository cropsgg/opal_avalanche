"use client";

import Link from "next/link";
import { UserButton } from "@clerk/nextjs";

export function ChatHeader() {
  return (
    <header className="bg-white border-b border-gray-200">
      <div className="mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="w-1/2 flex justify-end">
            <Link
              href="/dashboard"
              className="flex items-center space-x-3 group"
            >
              <span className="text-3xl font-medium tracking-tight text-black">
                Opal
              </span>
            </Link>
          </div>

          {/* User Button */}
          <div className="flex w-1/2 justify-end items-center">
            <UserButton
              appearance={{
                elements: {
                  userButtonAvatarBox: "w-8 h-8",
                },
              }}
            />
          </div>
        </div>
      </div>
    </header>
  );
}
