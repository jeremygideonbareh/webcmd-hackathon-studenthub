import * as React from "react";
import { AppShell } from "@/components/app-shell";
import { ErrorBoundary } from "@/components/error-boundary";
import { Hero } from "@/components/hero";
import { Reveal } from "@/components/reveal";
import { Skeleton } from "@/components/ui/skeleton";

// Code splitting / Lazy loading heavy section components
const Dashboard = React.lazy(() =>
  import("@/components/dashboard").then((m) => ({ default: m.Dashboard }))
);
const ServicesSection = React.lazy(() =>
  import("@/components/ui/services").then((m) => ({ default: m.ServicesSection }))
);

function SectionFallback() {
  return (
    <div className="space-y-6 py-6" aria-label="Loading section">
      <Skeleton className="h-24 w-full rounded-xl" />
      <Skeleton className="h-64 w-full rounded-xl" />
    </div>
  );
}

export default function App() {
  return (
    <AppShell>
      <Hero />

      <ErrorBoundary fallbackMessage="Failed to load dashboard metrics.">
        <React.Suspense fallback={<SectionFallback />}>
          <Reveal>
            <Dashboard />
          </Reveal>
        </React.Suspense>
      </ErrorBoundary>

      <ErrorBoundary fallbackMessage="Failed to load Atlas services section.">
        <React.Suspense fallback={<SectionFallback />}>
          <Reveal delay={0.1}>
            <ServicesSection />
          </Reveal>
        </React.Suspense>
      </ErrorBoundary>
    </AppShell>
  );
}
