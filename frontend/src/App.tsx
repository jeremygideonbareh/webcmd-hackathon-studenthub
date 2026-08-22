import * as React from "react";
import { AppShell } from "@/components/app-shell";
import { ErrorBoundary } from "@/components/error-boundary";
import { Hero } from "@/components/hero";
import { HowItWorks } from "@/components/how-it-works";
import { Level1AuthModal } from "@/components/level1-auth-modal";
import { Reveal } from "@/components/reveal";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { AuthProvider, useAuth } from "@/context/auth-context";

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

function MainContent() {
  const { isLevel1Authenticated } = useAuth();
  const [authModalOpen, setAuthModalOpen] = React.useState(false);

  return (
    <AppShell>
      <Hero />

      <Reveal>
        <HowItWorks />
      </Reveal>

      {isLevel1Authenticated ? (
        <>
          <ErrorBoundary fallbackMessage="Failed to load dashboard metrics.">
            <React.Suspense fallback={<SectionFallback />}>
              <Reveal delay={0.1}>
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
        </>
      ) : (
        <section className="my-12 rounded-2xl border bg-card p-8 text-center shadow-sm">
          <div className="mx-auto max-w-md space-y-4">
            <h3 className="text-2xl font-bold">Unlock Live Student Dashboard</h3>
            <p className="text-sm text-muted-foreground">
              Sign up or log in with your email to run live WebCMD scrapers for internships, scholarships, PGs/hostels, and student deals matching your stream.
            </p>
            <Button
              size="lg"
              onClick={() => setAuthModalOpen(true)}
              className="w-full font-semibold"
            >
              Sign Up / Login to Access Dashboard
            </Button>
          </div>
          <Level1AuthModal
            isOpen={authModalOpen}
            onClose={() => setAuthModalOpen(false)}
          />
        </section>
      )}
    </AppShell>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <MainContent />
    </AuthProvider>
  );
}
