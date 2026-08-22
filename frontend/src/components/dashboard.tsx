import * as React from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import {
  AlertTriangle,
  Briefcase,
  Home,
  KeyRound,
  Lock,
  MapPin,
  RefreshCw,
} from "lucide-react";

import { AdvisorTab } from "@/components/advisor-tab";
import { AttendanceSimulator } from "@/components/attendance-simulator";
import { DiscountsTab } from "@/components/discounts-tab";
import { ScholarshipsTab } from "@/components/scholarships-tab";
import { StudentAuthModal } from "@/components/student-auth-modal";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useAuth } from "@/context/auth-context";
import { fetchDigest, postFeedback } from "@/lib/api";
import type { Digest, Reaction, RiskLevel } from "@/lib/types";
import { cn } from "@/lib/utils";

const RISK_COLORS: Record<RiskLevel, string> = {
  SAFE: "#16a34a",
  CAUTION: "#d97706",
  WARNING: "#ea580c",
  DANGER: "#dc2626",
};

const RISK_BADGE: Record<RiskLevel, string> = {
  SAFE: "bg-green-100 text-green-800 border-green-200 dark:bg-green-950/80 dark:text-green-300 dark:border-green-800",
  CAUTION: "bg-amber-100 text-amber-800 border-amber-200 dark:bg-amber-950/80 dark:text-amber-300 dark:border-amber-800",
  WARNING: "bg-orange-100 text-orange-800 border-orange-200 dark:bg-orange-950/80 dark:text-orange-300 dark:border-orange-800",
  DANGER: "bg-red-100 text-red-800 border-red-200 dark:bg-red-950/80 dark:text-red-300 dark:border-red-800",
};

const FEEDBACK: { emoji: Reaction; label: string }[] = [
  { emoji: "👍", label: "Like" },
  { emoji: "👎", label: "Dislike" },
  { emoji: "⭐", label: "Save" },
  { emoji: "🚫", label: "Block" },
];

export function Dashboard() {
  const { isLevel2Authenticated } = useAuth();
  const [digest, setDigest] = React.useState<Digest | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [refreshing, setRefreshing] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [level2ModalOpen, setLevel2ModalOpen] = React.useState(false);

  const loadData = React.useCallback(async (isRefresh = false) => {
    if (isRefresh) setRefreshing(true);
    else setLoading(true);
    setError(null);

    try {
      const data = await fetchDigest();
      setDigest(data);
    } catch (e: any) {
      setError(e.message || "Failed to load dashboard data.");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  React.useEffect(() => {
    void loadData();
  }, [loadData]);

  if (loading) return <DashboardSkeleton />;

  if (error) {
    return (
      <Card className="my-8 border-destructive/50 bg-destructive/5">
        <CardContent className="flex flex-col items-center justify-center py-12 text-center">
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-destructive/10 text-destructive">
            <AlertTriangle className="h-6 w-6" aria-hidden="true" />
          </div>
          <h3 className="mt-4 text-lg font-semibold">Unable to load live dashboard</h3>
          <p className="mt-1 max-w-md text-sm text-muted-foreground">{error}</p>
          <Button
            variant="outline"
            onClick={() => void loadData(true)}
            className="mt-6 gap-2"
            disabled={refreshing}
          >
            <RefreshCw className={cn("h-4 w-4", refreshing && "animate-spin")} aria-hidden="true" />
            {refreshing ? "Retrying..." : "Retry Connection"}
          </Button>
        </CardContent>
      </Card>
    );
  }

  if (!digest) return null;

  return (
    <div className="space-y-8">
      {/* Top Header Controls */}
      <div className="flex items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight sm:text-3xl">Student Operating Dashboard</h2>
          <p className="text-sm text-muted-foreground">
            Portal analytics, AI career advisory, scholarships & student deals
          </p>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={() => void loadData(true)}
          disabled={refreshing}
          className="shrink-0 gap-2 focus-visible:ring-2 focus-visible:ring-ring"
          aria-label="Refresh dashboard data"
        >
          <RefreshCw className={cn("h-4 w-4", refreshing && "animate-spin")} aria-hidden="true" />
          <span className="hidden sm:inline">{refreshing ? "Refreshing..." : "Refresh"}</span>
        </Button>
      </div>

      <GpaStrip gpa={digest.gpa} />

      {/* Level 2 Protection Gate for Attendance Details */}
      <section id="attendance" className="scroll-mt-20">
        {isLevel2Authenticated ? (
          <>
            <AttendanceSection subjects={digest.attendance || []} />
            <div className="mt-8">
              <AttendanceSimulator subjects={digest.attendance || []} />
            </div>
          </>
        ) : (
          <Card className="border-primary/30 bg-card shadow-lg overflow-hidden">
            <div className="bg-gradient-to-r from-primary/10 via-primary/5 to-transparent p-6 sm:p-8">
              <div className="flex flex-col items-center text-center space-y-4">
                <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-primary/10 text-primary shadow-sm">
                  <Lock className="h-7 w-7" aria-hidden="true" />
                </div>
                <div className="space-y-1">
                  <Badge variant="outline" className="border-primary/30 text-primary">
                    Level 2 KP Student Portal Required
                  </Badge>
                  <h3 className="text-xl font-bold sm:text-2xl text-foreground">
                    Connect Student Portal Credentials to Unlock Attendance Risk & Class Simulator
                  </h3>
                  <p className="max-w-lg mx-auto text-xs sm:text-sm text-muted-foreground">
                    Direct integration with Christ University Knowledge Pro portal. Connect your student register number and KP password to sync real-time class attendance, calculate subject risk margins, and simulate classes to attend or miss.
                  </p>
                </div>
                <Button
                  size="lg"
                  onClick={() => setLevel2ModalOpen(true)}
                  className="gap-2 font-semibold shadow-md text-sm mt-2"
                >
                  <KeyRound className="h-4 w-4" aria-hidden="true" />
                  Connect KP Student Portal Credentials (Level 2)
                </Button>
              </div>
            </div>
          </Card>
        )}
      </section>

      <div id="advisor" className="scroll-mt-20">
        <AdvisorTab />
      </div>

      <div id="jobs" className="scroll-mt-20">
        <JobsSection
          jobs={digest.jobs || []}
          onFeedback={async (id, reaction) => {
            await postFeedback("job", id, reaction);
            await loadData(true);
          }}
        />
      </div>

      <div id="scholarships" className="scroll-mt-20">
        <ScholarshipsTab />
      </div>

      <div id="discounts" className="scroll-mt-20">
        <DiscountsTab />
      </div>

      <div id="housing" className="scroll-mt-20">
        <HousingSection
          listings={digest.housing || []}
          onFeedback={async (id, reaction) => {
            await postFeedback("housing", id, reaction);
            await loadData(true);
          }}
        />
      </div>

      <StudentAuthModal
        isOpen={level2ModalOpen}
        onClose={() => setLevel2ModalOpen(false)}
        onSuccess={() => void loadData(true)}
      />
    </div>
  );
}

function GpaStrip({ gpa }: { gpa: any }) {
  if (!gpa || typeof gpa.gpa !== "number") return null;
  return (
    <Card className="bg-primary/5 border-primary/20">
      <CardContent className="flex items-center justify-between p-4 sm:p-6">
        <div>
          <p className="text-xs uppercase tracking-wider text-muted-[#9a9a9a] font-semibold">
            Cumulative GPA
          </p>
          <p className="text-3xl font-black text-primary sm:text-4xl">{gpa.gpa.toFixed(2)}</p>
        </div>
        <div className="text-right text-xs text-muted-foreground">
          <p>Credits: <span className="font-semibold text-foreground">{gpa.credits || 120}</span></p>
          <p>Academic Standing: <span className="font-semibold text-green-500">Good</span></p>
        </div>
      </CardContent>
    </Card>
  );
}

function AttendanceSection({ subjects }: { subjects: any[] }) {
  if (!subjects.length) return null;

  const chartData = subjects.map((s) => ({
    name: s.code || s.name,
    percentage: s.percentage,
    risk: s.risk_level || "SAFE",
  }));

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-xl font-bold tracking-tight">Attendance Risk Radar</h3>
          <p className="text-xs text-muted-foreground">
            Subject-wise attendance tracking & minimum threshold margins
          </p>
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {subjects.map((subj) => (
          <Card key={subj.code || subj.name} className="overflow-hidden">
            <CardHeader className="p-4 pb-2">
              <div className="flex items-center justify-between">
                <Badge variant="outline" className={cn(RISK_BADGE[subj.risk_level as RiskLevel])}>
                  {subj.risk_level}
                </Badge>
                <span className="text-xs font-mono text-muted-foreground">{subj.code}</span>
              </div>
              <CardTitle className="text-sm font-semibold truncate mt-1">{subj.name}</CardTitle>
            </CardHeader>
            <CardContent className="p-4 pt-0 space-y-2">
              <div className="flex items-baseline justify-between">
                <span className="text-2xl font-bold">{subj.percentage}%</span>
                <span className="text-xs text-muted-foreground">
                  {subj.attended}/{subj.total} Held
                </span>
              </div>
              <div className="w-full bg-secondary h-2 rounded-full overflow-hidden">
                <div
                  className="h-full transition-all"
                  style={{
                    width: `${subj.percentage}%`,
                    backgroundColor: RISK_COLORS[subj.risk_level as RiskLevel],
                  }}
                />
              </div>
              <p className="text-[11px] text-muted-foreground">
                {subj.status_reason || "Attendance record verified via KP portal."}
              </p>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card className="p-4">
        <CardHeader className="px-0 pt-0">
          <CardTitle className="text-sm font-semibold">Attendance Percentage Distribution</CardTitle>
        </CardHeader>
        <CardContent className="px-0 pb-0 h-48">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="name" tick={{ fontSize: 10 }} />
              <YAxis domain={[0, 100]} tick={{ fontSize: 10 }} />
              <Tooltip />
              <Bar dataKey="percentage" radius={[4, 4, 0, 0]}>
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={RISK_COLORS[entry.risk as RiskLevel]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
}

function JobsSection({ jobs, onFeedback }: { jobs: any[]; onFeedback: (id: string, r: Reaction) => Promise<void> }) {
  if (!jobs.length) return null;

  return (
    <div className="space-y-4">
      <div>
        <h3 className="text-xl font-bold tracking-tight">WebCMD Matched Internships</h3>
        <p className="text-xs text-muted-foreground">
          Live Internshala & Indeed postings scored against your profile
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {jobs.map((job) => (
          <Card key={job.id} className="flex flex-col justify-between p-4">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Badge variant="secondary" className="text-[10px]">
                  Match {(job.match_score * 100).toFixed(0)}%
                </Badge>
                <span className="text-xs font-semibold text-primary">{job.stipend}</span>
              </div>
              <h4 className="font-bold text-sm leading-snug">{job.title}</h4>
              <p className="text-xs text-muted-foreground">{job.company}</p>
              <p className="text-[11px] text-muted-foreground line-clamp-2">{job.match_reason}</p>
            </div>

            <div className="mt-4 pt-3 border-t flex items-center justify-between">
              <div className="flex gap-1">
                {FEEDBACK.map((f) => (
                  <button
                    key={f.emoji}
                    onClick={() => void onFeedback(job.id, f.emoji)}
                    className="p-1 text-xs hover:scale-125 transition-transform"
                    title={f.label}
                  >
                    {f.emoji}
                  </button>
                ))}
              </div>
              <a
                href={job.url}
                target="_blank"
                rel="noreferrer"
                className="text-xs font-semibold text-primary hover:underline flex items-center gap-1"
              >
                Apply <Briefcase className="h-3 w-3" />
              </a>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}

function HousingSection({ listings, onFeedback }: { listings: any[]; onFeedback: (id: string, r: Reaction) => Promise<void> }) {
  if (!listings.length) return null;

  return (
    <div className="space-y-4">
      <div>
        <h3 className="text-xl font-bold tracking-tight">Campus Housing & PGs</h3>
        <p className="text-xs text-muted-foreground">
          Live NoBroker & Stanza listings near campus
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {listings.map((item) => (
          <Card key={item.id} className="flex flex-col justify-between p-4">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Badge variant="outline" className="text-[10px]">
                  {item.furnished}
                </Badge>
                <span className="text-xs font-bold text-emerald-600">{item.price}</span>
              </div>
              <h4 className="font-bold text-sm leading-snug">{item.title}</h4>
              <p className="text-xs text-muted-foreground flex items-center gap-1">
                <MapPin className="h-3 w-3" /> {item.location}
              </p>
            </div>

            <div className="mt-4 pt-3 border-t flex items-center justify-between">
              <div className="flex gap-1">
                {FEEDBACK.map((f) => (
                  <button
                    key={f.emoji}
                    onClick={() => void onFeedback(item.id, f.emoji)}
                    className="p-1 text-xs hover:scale-125 transition-transform"
                    title={f.label}
                  >
                    {f.emoji}
                  </button>
                ))}
              </div>
              <a
                href={item.url}
                target="_blank"
                rel="noreferrer"
                className="text-xs font-semibold text-primary hover:underline flex items-center gap-1"
              >
                View Deal <Home className="h-3 w-3" />
              </a>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}

function DashboardSkeleton() {
  return (
    <div className="space-y-6">
      <Skeleton className="h-20 w-full rounded-xl" />
      <div className="grid gap-4 sm:grid-cols-3">
        <Skeleton className="h-36 rounded-xl" />
        <Skeleton className="h-36 rounded-xl" />
        <Skeleton className="h-36 rounded-xl" />
      </div>
    </div>
  );
}
