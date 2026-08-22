import * as React from "react";
import { KeyRound, ShieldCheck, Sparkles, UserCheck, UserPlus } from "lucide-react";
import { WorkPageHero } from "@/components/ui/work-page-hero";
import { Button } from "@/components/ui/button";
import { Level1AuthModal } from "@/components/level1-auth-modal";
import { StudentAuthModal } from "@/components/student-auth-modal";
import { useAuth } from "@/context/auth-context";

export function Hero() {
  const { user, isLevel1Authenticated } = useAuth();
  const [level1Open, setLevel1Open] = React.useState(false);
  const [level2Open, setLevel2Open] = React.useState(false);

  return (
    <div className="relative">
      {/* WorkPageHero Scroll-Expand Kinetic Video Component */}
      <WorkPageHero
        videoSrc="https://res.cloudinary.com/dsuwzuaxp/video/upload/video1_horxtt.mp4"
        topWord="atlas"
        rightWord="student"
        bottomWord="hub"
        accentColor="#f97316"
        textColor="#09090b"
        backgroundColor="#fafafa"
        showClocks={true}
        clocks={[
          { tz: "Asia/Kolkata", label: "INDIA" },
          { tz: "America/New_York", label: "NEW YORK" },
          { tz: "Asia/Dubai", label: "DUBAI" },
        ]}
      />

      {/* Hero Action Bar & Multi-Level Login Controls */}
      <div className="relative z-30 mx-auto max-w-4xl px-4 py-8 text-center sm:py-12">
        <div className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/10 px-4 py-1.5 text-xs font-semibold text-primary">
          <Sparkles className="h-3.5 w-3.5" aria-hidden="true" />
          <span>Christ University KP Portal & SheerID Verified</span>
        </div>

        <h1 className="mt-4 text-3xl font-bold tracking-tight sm:text-5xl lg:text-6xl text-foreground">
          Your All-In-One Student Intelligence Hub
        </h1>
        <p className="mt-3 text-base text-muted-foreground sm:text-xl max-w-2xl mx-auto">
          Portal attendance risk radar, AI skills advisor for Engineering, Psychology, BBA, and MBA, scholarships, and verified student discounts.
        </p>

        <div className="mt-6 flex flex-wrap items-center justify-center gap-3">
          {isLevel1Authenticated ? (
            <>
              <Button
                size="lg"
                onClick={() => setLevel2Open(true)}
                className="gap-2 font-semibold text-sm shadow-md"
              >
                <UserCheck className="h-4 w-4 text-green-400" aria-hidden="true" />
                Level 1 Verified: {user?.email} ({user?.stream})
              </Button>

              <a href="#attendance">
                <Button variant="outline" size="lg" className="gap-2 text-sm">
                  <KeyRound className="h-4 w-4" aria-hidden="true" />
                  Connect Level 2 KP Portal Credentials
                </Button>
              </a>
            </>
          ) : (
            <Button
              size="lg"
              onClick={() => setLevel1Open(true)}
              className="gap-2 font-semibold text-sm shadow-md"
            >
              <UserPlus className="h-4 w-4" aria-hidden="true" />
              Sign Up / Student Login to Unlock Features
            </Button>
          )}

          <a href="#how-it-works">
            <Button variant="ghost" size="lg" className="gap-2 text-sm">
              <ShieldCheck className="h-4 w-4" aria-hidden="true" />
              How Atlas Works
            </Button>
          </a>
        </div>
      </div>

      <Level1AuthModal
        isOpen={level1Open}
        onClose={() => setLevel1Open(false)}
      />

      <StudentAuthModal
        isOpen={level2Open}
        onClose={() => setLevel2Open(false)}
        onSuccess={() => {}}
      />
    </div>
  );
}
