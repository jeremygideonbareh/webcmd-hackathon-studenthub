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
    <div id="home" className="relative">
      {/* WorkPageHero Aalto Display Scroll-Expand Kinetic Video Component */}
      <WorkPageHero
        videoSrc="https://res.cloudinary.com/dsuwzuaxp/video/upload/video1_horxtt.mp4"
        topWord="ATLAS"
        rightWord="STUDENT"
        bottomWord="HUB"
        backgroundColor={undefined}
        showClocks={true}
        clocks={[
          { tz: "Asia/Kolkata", label: "INDIA" },
          { tz: "America/New_York", label: "NEW YORK" },
          { tz: "Asia/Dubai", label: "DUBAI" },
        ]}
      />

      {/* Hero Action Bar & Multi-Level Login Controls */}
      <div className="relative z-30 mx-auto max-w-4xl px-4 py-8 text-center sm:py-12">
        <div className="inline-flex items-center gap-2 rounded-full border border-[#FF9398]/30 bg-gradient-to-r from-[#FF9398]/10 via-[#D14836]/10 to-[#ECD06F]/10 px-4 py-1.5 text-xs font-semibold text-[#FF9398]">
          <Sparkles className="h-3.5 w-3.5" aria-hidden="true" />
          <span>Christ University KP Portal & SheerID Verified</span>
        </div>

        <h1 className="mt-4 text-3xl font-black tracking-tight sm:text-5xl lg:text-6xl text-foreground font-display">
          Your All-In-One <span className="gradient-text">Student Intelligence Hub</span>
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
                className="gap-2 font-semibold text-sm shadow-md bg-gradient-to-r from-[#D14836] to-[#FF9398] hover:opacity-95 text-white"
              >
                <UserCheck className="h-4 w-4 text-white" aria-hidden="true" />
                Level 1 Verified: {user?.email} ({user?.stream})
              </Button>

              <a href="#attendance">
                <Button variant="outline" size="lg" className="gap-2 text-sm border-white/20 hover:bg-white/10">
                  <KeyRound className="h-4 w-4 text-[#ECD06F]" aria-hidden="true" />
                  Connect Level 2 KP Portal Credentials
                </Button>
              </a>
            </>
          ) : (
            <Button
              size="lg"
              onClick={() => setLevel1Open(true)}
              className="gap-2 font-semibold text-sm shadow-md bg-gradient-to-r from-[#D14836] via-[#FF9398] to-[#D14836] hover:opacity-95 text-white"
            >
              <UserPlus className="h-4 w-4" aria-hidden="true" />
              Sign Up / Student Login to Unlock Features
            </Button>
          )}

          <a href="#how-it-works">
            <Button variant="ghost" size="lg" className="gap-2 text-sm text-muted-foreground hover:text-foreground">
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
