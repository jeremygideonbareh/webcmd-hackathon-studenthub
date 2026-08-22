import * as React from "react";
import { SterlingGateKineticNavigation } from "@/components/ui/sterling-gate-kinetic-navigation";

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-background relative pb-12">
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-50 focus:rounded-md focus:bg-primary focus:px-4 focus:py-2 focus:text-primary-foreground focus:shadow-lg focus:outline-none focus:ring-2 focus:ring-ring"
      >
        Skip to main content
      </a>

      {/* Fullscreen Sterling Gate Kinetic Navigation Header & Menu */}
      <SterlingGateKineticNavigation />

      {/* Main Content Viewport */}
      <main id="main-content" className="mx-auto max-w-6xl px-4 py-6 sm:px-6 lg:px-8">
        {children}
      </main>
    </div>
  );
}
