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
  CheckCircle2,
  Clock,
  GraduationCap,
  Home,
  MapPin,
  RefreshCw,
} from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { fetchDigest, postFeedback } from "@/lib/api";
import { calculateRisk } from "@/lib/math";
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
  const [digest, setDigest] = React.useState<Digest | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [refreshing, setRefreshing] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

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
          <h2 className="text-2xl font-bold tracking-tight sm:text-3xl">Student Overview</h2>
          <p className="text-sm text-muted-foreground">
            Live metrics & personalized recommendations
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
      <AttendanceSection subjects={digest.attendance || []} />
      <JobsSection
        jobs={digest.jobs || []}
        onFeedback={async (id, reaction) => {
          const res = await postFeedback("job", id, reaction);
          setDigest((prev) =>
            prev ? { ...prev, weights: res.weights } : prev
          );
        }}
      />
      <HousingSection listings={digest.housing || []} />
    </div>
  );
}

function GpaStrip({ gpa }: { gpa: Digest["gpa"] }) {
  if (!gpa?.current_cgpa) return null;
  return (
    <Card id="home" className="overflow-hidden border bg-card shadow-sm transition-shadow hover:shadow-md">
      <CardContent className="flex flex-wrap items-center justify-between gap-4 py-5">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            Current Cumulative GPA
          </p>
          <div className="mt-1 flex items-baseline gap-3">
            <span className="text-3xl font-bold tracking-tight sm:text-4xl text-foreground">
              {gpa.current_cgpa}
            </span>
            <Badge variant="outline" className="capitalize text-xs font-medium">
              Trend: {gpa.gpa_trend ?? "stable"}
            </Badge>
          </div>
        </div>
        <div className="text-left sm:text-right">
          <p className="text-sm font-medium text-foreground">
            Semester GPA: <span className="font-semibold text-primary">{gpa.semester_gpa ?? "—"}</span>
          </p>
          <p className="mt-0.5 text-xs text-muted-foreground">
            Student ID: {gpa.student_id ?? "Authenticated"}
          </p>
        </div>
      </CardContent>
    </Card>
  );
}

function AttendanceSection({
  subjects,
}: {
  subjects: Digest["attendance"];
}) {
  const rows = React.useMemo(() => {
    return subjects.map((s) => {
      const r = calculateRisk(s.classes_present, s.classes_total);
      return { ...s, ...r };
    });
  }, [subjects]);

  const chartData = React.useMemo(() => {
    return rows.map((s) => ({
      name: s.code,
      attended: s.classes_present,
      total: s.classes_total,
      pct: s.current_pct,
      risk: s.risk_level,
    }));
  }, [rows]);

  return (
    <section id="attendance" aria-labelledby="attendance-heading">
      <Card className="shadow-sm">
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <div>
            <CardTitle id="attendance-heading" className="text-xl sm:text-2xl">
              Attendance Risk Radar
            </CardTitle>
            <CardDescription className="text-sm">
              Skip/attend projections calculated from your live Knowledge Pro portal data
            </CardDescription>
          </div>
          <GraduationCap className="h-6 w-6 text-muted-foreground shrink-0" aria-hidden="true" />
        </CardHeader>

        <CardContent className="space-y-6 pt-4">
          {subjects.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <GraduationCap className="h-12 w-12 text-muted-foreground/50" aria-hidden="true" />
              <p className="mt-3 text-base font-medium">No attendance records found</p>
              <p className="mt-1 text-xs text-muted-foreground">
                Check back after your portal sync completes.
              </p>
            </div>
          ) : (
            <>
              <div className="h-64 sm:h-72 w-full min-w-[280px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                    <CartesianGrid strokeDasharray="3 3" className="stroke-muted/60" />
                    <XAxis
                      dataKey="name"
                      className="text-xs"
                      tick={{ fontSize: 11 }}
                      interval={0}
                    />
                    <YAxis className="text-xs" tick={{ fontSize: 11 }} />
                    <Tooltip
                      formatter={(value: any) => [`${value} classes`, "Attended"]}
                      labelFormatter={(label) => `Subject: ${label}`}
                      contentStyle={{
                        borderRadius: "8px",
                        boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
                        fontSize: "12px",
                      }}
                      cursor={{ fill: "rgba(0,0,0,0.04)" }}
                    />
                    <Bar dataKey="attended" name="Attended" radius={[4, 4, 0, 0]}>
                      {chartData.map((d) => (
                        <Cell key={d.name} fill={RISK_COLORS[d.risk] ?? "#888"} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                {rows.map((s) => (
                  <article
                    key={s.code}
                    className="rounded-xl border p-4 transition-all hover:shadow-sm"
                    style={{ borderLeftWidth: "4px", borderLeftColor: RISK_COLORS[s.risk_level] }}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="min-w-0">
                        <p className="font-mono text-xs font-semibold text-muted-foreground uppercase">
                          {s.code}
                        </p>
                        <h4 className="font-semibold text-sm sm:text-base leading-snug break-words">
                          {s.name}
                        </h4>
                      </div>
                      <Badge className={cn("shrink-0 font-bold border", RISK_BADGE[s.risk_level] ?? "")}>
                        {s.risk_level}
                      </Badge>
                    </div>

                    <div className="mt-3 flex items-baseline justify-between">
                      <p className="text-2xl font-bold tracking-tight" style={{ color: RISK_COLORS[s.risk_level] }}>
                        {s.current_pct}%
                      </p>
                      <span className="text-xs font-medium text-muted-foreground">
                        {s.classes_present} / {s.classes_total} attended
                      </span>
                    </div>

                    <div className="mt-2 flex flex-wrap gap-2 text-xs">
                      <span className="rounded bg-muted px-2 py-0.5 font-medium">
                        Can skip: <strong className="text-foreground">{s.classes_can_skip}</strong>
                      </span>
                      <span className="rounded bg-muted px-2 py-0.5 font-medium">
                        Must attend: <strong className="text-foreground">{s.classes_must_attend}</strong>
                      </span>
                    </div>

                    <p className="mt-3 text-xs leading-relaxed text-muted-foreground border-t pt-2">
                      {s.projection}
                    </p>
                  </article>
                ))}
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </section>
  );
}

function JobsSection({
  jobs,
  onFeedback,
}: {
  jobs: Digest["jobs"];
  onFeedback: (id: string, reaction: Reaction) => Promise<void>;
}) {
  const [learned, setLearned] = React.useState<Record<string, string>>({});

  return (
    <section id="jobs" aria-labelledby="jobs-heading">
      <Card className="shadow-sm">
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <div>
            <CardTitle id="jobs-heading" className="text-xl sm:text-2xl">
              Matched Internships
            </CardTitle>
            <CardDescription className="text-sm">
              TF-IDF scored by resume skills & GPA. Click feedback buttons to teach your preferences.
            </CardDescription>
          </div>
          <Briefcase className="h-6 w-6 text-muted-foreground shrink-0" aria-hidden="true" />
        </CardHeader>

        <CardContent className="space-y-4 pt-4">
          {jobs.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <Briefcase className="h-12 w-12 text-muted-foreground/50" aria-hidden="true" />
              <p className="mt-3 text-base font-medium">No matched internships found</p>
              <p className="mt-1 text-xs text-muted-foreground">
                We are actively scanning job boards for roles matching your resume.
              </p>
            </div>
          ) : (
            jobs.map((job) => {
              const score = Math.round(job.match_score * 100);
              return (
                <article
                  key={job.id}
                  className="rounded-xl border p-4 sm:p-5 transition-colors hover:bg-accent/30"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="min-w-0 flex-1">
                      <h4 className="font-semibold text-base sm:text-lg text-foreground break-words">
                        {job.title}
                      </h4>
                      <p className="text-sm font-medium text-muted-foreground">
                        {job.company} {job.stipend ? `· ${job.stipend}` : ""}
                      </p>
                      {job.location && (
                        <p className="mt-1 flex items-center gap-1.5 text-xs text-muted-foreground">
                          <MapPin className="h-3.5 w-3.5 shrink-0" aria-hidden="true" />
                          {job.location}
                        </p>
                      )}
                    </div>
                    <span className="shrink-0 rounded-full border border-primary/20 bg-primary/10 px-3 py-1 text-xs font-bold text-primary">
                      {score}% Match
                    </span>
                  </div>

                  {job.match_reason && (
                    <p className="mt-2 text-xs text-muted-foreground leading-relaxed bg-muted/40 rounded-lg p-2.5">
                      💡 {job.match_reason}
                    </p>
                  )}

                  <div className="mt-4 flex items-center justify-between flex-wrap gap-3 border-t pt-3">
                    <div className="flex items-center gap-1.5 flex-wrap">
                      <span className="text-xs text-muted-foreground font-medium mr-1">Feedback:</span>
                      {FEEDBACK.map(({ emoji, label }) => (
                        <button
                          key={emoji}
                          type="button"
                          onClick={() => {
                            void onFeedback(job.id, emoji);
                            setLearned((p) => ({ ...p, [job.id]: label }));
                          }}
                          className="flex min-h-[44px] min-w-[44px] items-center justify-center rounded-lg border bg-background text-base transition-all hover:scale-105 hover:bg-accent focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                          aria-label={`Mark internship "${job.title}" as ${label}`}
                          title={`Mark as ${label}`}
                        >
                          {emoji}
                        </button>
                      ))}
                    </div>

                    {learned[job.id] && (
                      <span className="flex items-center gap-1.5 text-xs font-medium text-green-600 dark:text-green-400 bg-green-50 dark:bg-green-950/40 px-2.5 py-1 rounded-md">
                        <CheckCircle2 className="h-3.5 w-3.5" aria-hidden="true" />
                        Preference saved: {learned[job.id]}
                      </span>
                    )}

                    {job.url && (
                      <a
                        href={job.url}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex min-h-[44px] items-center gap-1 text-xs font-semibold text-primary hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                      >
                        Apply / Details &rarr;
                      </a>
                    )}
                  </div>
                </article>
              );
            })
          )}
        </CardContent>
      </Card>
    </section>
  );
}

function HousingSection({
  listings,
}: {
  listings: Digest["housing"];
}) {
  return (
    <section id="housing" aria-labelledby="housing-heading">
      <Card className="shadow-sm">
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <div>
            <CardTitle id="housing-heading" className="text-xl sm:text-2xl">
              Housing Near Campus
            </CardTitle>
            <CardDescription className="text-sm">
              Affordable rental properties and room options near your institution
            </CardDescription>
          </div>
          <Home className="h-6 w-6 text-muted-foreground shrink-0" aria-hidden="true" />
        </CardHeader>

        <CardContent className="pt-4">
          {listings.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <Home className="h-12 w-12 text-muted-foreground/50" aria-hidden="true" />
              <p className="mt-3 text-base font-medium">No housing listings found</p>
              <p className="mt-1 text-xs text-muted-foreground">
                NoBroker listings will appear here shortly.
              </p>
            </div>
          ) : (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {listings.map((h) => (
                <article
                  key={h.id}
                  className="flex flex-col justify-between rounded-xl border p-4 sm:p-5 transition-all hover:shadow-md bg-card"
                >
                  <div>
                    <h4 className="font-semibold text-base leading-snug break-words text-foreground">
                      {h.title}
                    </h4>
                    <p className="mt-2 text-xl font-bold text-primary">{h.price}</p>
                    {h.location && (
                      <p className="mt-1.5 flex items-center gap-1.5 text-xs text-muted-foreground">
                        <MapPin className="h-3.5 w-3.5 shrink-0" aria-hidden="true" />
                        {h.location}
                      </p>
                    )}
                    {h.furnished && (
                      <Badge variant="secondary" className="mt-2 text-xs font-normal">
                        {h.furnished}
                      </Badge>
                    )}
                  </div>

                  {h.url && (
                    <a
                      href={h.url}
                      target="_blank"
                      rel="noreferrer"
                      aria-label={`View details for housing: ${h.title}`}
                      className="mt-4 inline-flex min-h-[44px] items-center gap-1.5 text-xs font-semibold text-primary hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                    >
                      <Clock className="h-3.5 w-3.5" aria-hidden="true" />
                      View Listing Details
                    </a>
                  )}
                </article>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </section>
  );
}

function DashboardSkeleton() {
  return (
    <div className="space-y-8" role="status" aria-label="Loading dashboard metrics">
      <Skeleton className="h-24 w-full rounded-xl" />
      <Skeleton className="h-96 w-full rounded-xl" />
      <div className="grid gap-4 sm:grid-cols-2">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-44 w-full rounded-xl" />
        ))}
      </div>
      <Skeleton className="h-64 w-full rounded-xl" />
    </div>
  );
}
