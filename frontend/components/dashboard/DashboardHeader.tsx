"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Scale, Plus, Search, Bell, MessageSquare } from "lucide-react";
import { UserButton } from "@clerk/nextjs";

export function DashboardHeader() {
  return (
    <header
      style={{ backgroundColor: "white", borderBottom: "1px solid #D1D5DB" }}
    >
      <div className=" mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="w-1/2 flex justify-end ">
            <Link
              href="/dashboard"
              className="flex items-center space-x-3 group"
            >
              <span className="text-3xl font-medium tracking-tight">Opal</span>
            </Link>
          </div>

          {/* Actions */}
          <div className="flex w-1/2 justify-end items-center space-x-4">
            <Link href="/chat">
              <Button
                variant="ghost"
                size="icon"
                className="hover:bg-gray-100"
                style={{ color: "#6B7280" }}
              >
                <MessageSquare className="h-4 w-4" />
              </Button>
            </Link>
            <Button
              variant="ghost"
              size="icon"
              className="hover:bg-gray-100"
              style={{ color: "#6B7280" }}
            >
              <Bell className="h-4 w-4" />
            </Button>
            <UserButton afterSignOutUrl="/" />
          </div>
        </div>
      </div>
    </header>
  );
}
