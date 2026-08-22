import * as React from "react";
import { KeyRound, ShieldCheck, Sparkles, UserCheck } from "lucide-react";
import { WorkPageHero } from "@/components/ui/work-page-hero";
import { Button } from "@/components/ui/button";
import { StudentAuthModal } from "@/components/student-auth-modal";

export function Hero() {
  const [authOpen, setAuthOpen] = React.useState(false);
  const [studentInfo, setStudentInfo] = React.useState<{ email: string; university: string } | null>(() => {
    try {
      const saved = localStorage.getItem("atlas_user_session");
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });

  React.useEffect(() => {
    if (!studentInfo) {
      fetch("/api/auth/session")
        .then((res) => res.json())
        .then((data) => {
          if (data?.session?.email) {
            const sess = { email: data.session.email, university: data.session.university };
            setStudentInfo(sess);
            localStorage.setItem("atlas_user_session", JSON.stringify(sess));
          }
        })
        .catch(() => {});
    }
  }, [studentInfo]);

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

      {/* Hero Action Bar & Quick Login */}
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
          <Button
            size="lg"
            onClick={() => setAuthOpen(true)}
            className="gap-2 font-semibold text-sm shadow-md"
          >
            {studentInfo ? (
              <>
                <UserCheck className="h-4 w-4 text-green-400" aria-hidden="true" />
                Verified: {studentInfo.email}
              </>
            ) : (
              <>
                <KeyRound className="h-4 w-4" aria-hidden="true" />
                Login to Student Portal
              </>
            )}
          </Button>

          <a href="#how-it-works">
            <Button variant="outline" size="lg" className="gap-2 text-sm">
              <ShieldCheck className="h-4 w-4" aria-hidden="true" />
              How Atlas Works
            </Button>
          </a>
        </div>
      </div>

      <StudentAuthModal
        isOpen={authOpen}
        onClose={() => setAuthOpen(false)}
        onSuccess={(email, university) => {
          const sess = { email, university };
          setStudentInfo(sess);
          localStorage.setItem("atlas_user_session", JSON.stringify(sess));
          fetch("/api/auth/session", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(sess),
          }).catch(() => {});
        }}
      />
    </div>
  );
}
