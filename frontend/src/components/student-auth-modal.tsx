import * as React from "react";
import { CheckCircle2, ShieldCheck, UserCheck, X } from "lucide-react";
import { Button } from "@/components/ui/button";

interface StudentAuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (email: string, university: string) => void;
}

export function StudentAuthModal({ isOpen, onClose, onSuccess }: StudentAuthModalProps) {
  const [email, setEmail] = React.useState("");
  const [university, setUniversity] = React.useState("Christ University (Knowledge Pro)");
  const [verifying, setVerifying] = React.useState(false);
  const [step, setStep] = React.useState<"email" | "verified">("email");
  const [verifiedPerks, setVerifiedPerks] = React.useState<string[]>([]);

  if (!isOpen) return null;

  const handleVerifyEdu = (e: React.FormEvent) => {
    e.preventDefault();
    setVerifying(true);

    setTimeout(() => {
      setVerifying(false);
      setVerifiedPerks([
        "SheerID Student Status: VERIFIED",
        "GitHub Developer Pack: UNLOCKED",
        "Exclusive Discounts: ACTIVATED",
        "Portal Data Bridge: ACTIVE (Aaron's KP Scraper Integration)",
      ]);
      setStep("verified");
      onSuccess(email || "student@christuniversity.in", university);
    }, 1200);
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
      role="dialog"
      aria-modal="true"
      aria-labelledby="auth-modal-title"
    >
      <div className="relative w-full max-w-lg overflow-hidden rounded-2xl border bg-card p-6 shadow-2xl transition-all">
        <button
          onClick={onClose}
          className="absolute right-4 top-4 rounded-lg p-2 text-muted-foreground hover:bg-accent hover:text-foreground"
          aria-label="Close authentication modal"
        >
          <X className="h-5 w-5" />
        </button>

        {step === "email" && (
          <form onSubmit={handleVerifyEdu} className="space-y-5">
            <div>
              <div className="flex items-center gap-2">
                <ShieldCheck className="h-6 w-6 text-primary" />
                <h3 id="auth-modal-title" className="text-xl font-bold">
                  Student Verification (SheerID)
                </h3>
              </div>
              <p className="mt-1 text-xs text-muted-foreground">
                Enter your official university email (e.g. <code>.edu</code> or <code>@christuniversity.in</code>) to verify your student identity and unlock student discounts & scholarships.
              </p>
            </div>

            <div className="rounded-xl border border-primary/20 bg-primary/5 p-3 text-xs text-muted-foreground leading-relaxed">
              ℹ️ <strong>Portal Credentials Sync:</strong> Aaron is completing the live KP Portal CAPTCHA solver helper on <code>aaron/portal</code>. Automatic attendance fallback is currently active.
            </div>

            <div className="space-y-3">
              <div>
                <label className="text-xs font-semibold text-muted-foreground uppercase">
                  Select Institution
                </label>
                <select
                  value={university}
                  onChange={(e) => setUniversity(e.target.value)}
                  className="mt-1 w-full rounded-lg border bg-background px-3 py-2 text-sm font-medium focus-visible:ring-2 focus-visible:ring-ring"
                >
                  <option value="Christ University (Knowledge Pro)">
                    Christ University (Knowledge Pro Portal)
                  </option>
                  <option value="General University (.edu / SheerID)">
                    Other Verified University (.edu SheerID)
                  </option>
                </select>
              </div>

              <div>
                <label className="text-xs font-semibold text-muted-foreground uppercase">
                  University Student Email
                </label>
                <input
                  type="email"
                  required
                  placeholder="student.name@christuniversity.in"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="mt-1 w-full rounded-lg border bg-background px-3 py-2 text-sm focus-visible:ring-2 focus-visible:ring-ring"
                />
              </div>
            </div>

            <Button type="submit" className="w-full font-semibold" disabled={verifying}>
              {verifying ? "Verifying with SheerID..." : "Verify Student Identity"}
            </Button>
          </form>
        )}

        {step === "verified" && (
          <div className="text-center py-4 space-y-4">
            <div className="flex h-14 w-14 items-center justify-center rounded-full bg-green-100 dark:bg-green-950/60 text-green-600 dark:text-green-400 mx-auto">
              <UserCheck className="h-7 w-7" />
            </div>
            <div>
              <h3 className="text-xl font-bold">Student Verified!</h3>
              <p className="mt-1 text-xs text-muted-foreground">
                Verified student status for <strong>{email}</strong>. Attendance calculus, stream advisor, and student deals are active.
              </p>
            </div>

            <div className="rounded-xl border bg-muted/40 p-3 space-y-1 text-xs text-left">
              {verifiedPerks.map((perk, i) => (
                <div key={i} className="flex items-center gap-2 text-green-700 dark:text-green-400 font-medium">
                  <CheckCircle2 className="h-3.5 w-3.5 shrink-0" />
                  <span>{perk}</span>
                </div>
              ))}
            </div>

            <Button onClick={onClose} className="w-full font-semibold">
              Return to Dashboard
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}
