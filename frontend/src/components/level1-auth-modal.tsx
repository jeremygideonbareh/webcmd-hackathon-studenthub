import * as React from "react";
import { UserPlus, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/context/auth-context";
import type { StreamType } from "@/lib/types";

const STREAMS: StreamType[] = ["Engineering", "Psychology", "BBA", "MBA"];

interface Level1AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

export function Level1AuthModal({ isOpen, onClose, onSuccess }: Level1AuthModalProps) {
  const { loginLevel1 } = useAuth();
  const [email, setEmail] = React.useState("");
  const [university] = React.useState("Christ University (Knowledge Pro)");
  const [stream, setStream] = React.useState<StreamType>("Engineering");
  const [locality, setLocality] = React.useState("Koramangala");
  const [gpa, setGpa] = React.useState("8.2");
  const [skills, setSkills] = React.useState("Python, Git, SQL, Data Structures");
  const [loading, setLoading] = React.useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    const skillsArray = skills
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean);

    const userDetails = {
      email,
      university,
      stream,
      locality,
      gpa: parseFloat(gpa) || 8.0,
      skills: skillsArray,
    };

    try {
      await fetch("/api/live/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(userDetails),
      });

      loginLevel1(userDetails);
      setLoading(false);
      onClose();
      if (onSuccess) onSuccess();
    } catch (err) {
      console.error("Live WebCMD search error:", err);
      loginLevel1(userDetails);
      setLoading(false);
      onClose();
      if (onSuccess) onSuccess();
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm"
      role="dialog"
      aria-modal="true"
      aria-labelledby="level1-modal-title"
    >
      <div className="relative w-full max-w-lg overflow-hidden rounded-2xl border bg-card p-6 shadow-2xl transition-all">
        <button
          onClick={onClose}
          className="absolute right-4 top-4 rounded-lg p-2 text-muted-foreground hover:bg-accent hover:text-foreground"
          aria-label="Close authentication modal"
        >
          <X className="h-5 w-5" />
        </button>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <div className="flex items-center gap-2">
              <UserPlus className="h-6 w-6 text-primary" />
              <h3 id="level1-modal-title" className="text-xl font-bold">
                Student Sign Up & Live WebCMD Search
              </h3>
            </div>
            <p className="mt-1 text-xs text-muted-foreground">
              Level 1 Authentication: Enter your student details to initiate live WebCMD scraping for internships, scholarships, PGs/hostels, and student deals.
            </p>
          </div>

          <div className="space-y-3 text-xs">
            <div>
              <label className="font-semibold uppercase text-muted-foreground">
                Student Email (.edu or @christuniversity.in)
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

            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="font-semibold uppercase text-muted-foreground">
                  Academic Stream
                </label>
                <select
                  value={stream}
                  onChange={(e) => setStream(e.target.value as StreamType)}
                  className="mt-1 w-full rounded-lg border bg-background px-3 py-2 text-sm font-medium focus-visible:ring-2 focus-visible:ring-ring"
                >
                  {STREAMS.map((s) => (
                    <option key={s} value={s}>
                      {s}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="font-semibold uppercase text-muted-foreground">
                  Current CGPA
                </label>
                <input
                  type="number"
                  step="0.1"
                  min="0"
                  max="10"
                  required
                  value={gpa}
                  onChange={(e) => setGpa(e.target.value)}
                  className="mt-1 w-full rounded-lg border bg-background px-3 py-2 text-sm focus-visible:ring-2 focus-visible:ring-ring"
                />
              </div>
            </div>

            <div>
              <label className="font-semibold uppercase text-muted-foreground">
                Campus Locality / PG Search Target Area
              </label>
              <input
                type="text"
                required
                placeholder="e.g. Koramangala, BTM Layout, Christ University"
                value={locality}
                onChange={(e) => setLocality(e.target.value)}
                className="mt-1 w-full rounded-lg border bg-background px-3 py-2 text-sm focus-visible:ring-2 focus-visible:ring-ring"
              />
            </div>

            <div>
              <label className="font-semibold uppercase text-muted-foreground">
                Your Core Competencies & Skills (comma-separated)
              </label>
              <input
                type="text"
                required
                placeholder="e.g. Python, SPSS, Financial Modeling, SQL"
                value={skills}
                onChange={(e) => setSkills(e.target.value)}
                className="mt-1 w-full rounded-lg border bg-background px-3 py-2 text-sm focus-visible:ring-2 focus-visible:ring-ring"
              />
            </div>
          </div>

          <div className="rounded-xl border border-primary/20 bg-primary/5 p-3 text-[11px] text-muted-foreground">
            ⚡ <strong>No Buffer Data:</strong> Submitting will immediately run live WebCMD scrapers for housing near {locality}, internships matching your skills, and stream deals for {stream}.
          </div>

          <Button type="submit" className="w-full font-semibold" disabled={loading}>
            {loading ? "Executing WebCMD Live Scrape..." : "Sign Up & Unlock Live Student Operating System"}
          </Button>
        </form>
      </div>
    </div>
  );
}
