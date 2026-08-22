import * as React from "react";
import { Calculator, Minus, Plus } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { calculateRisk } from "@/lib/math";
import type { RiskLevel, SubjectAttendance } from "@/lib/types";

const RISK_BADGE: Record<RiskLevel, string> = {
  SAFE: "bg-green-100 text-green-800 border-green-200 dark:bg-green-950/80 dark:text-green-300 dark:border-green-800",
  CAUTION: "bg-amber-100 text-amber-800 border-amber-200 dark:bg-amber-950/80 dark:text-amber-300 dark:border-amber-800",
  WARNING: "bg-orange-100 text-orange-800 border-orange-200 dark:bg-orange-950/80 dark:text-orange-300 dark:border-orange-800",
  DANGER: "bg-red-100 text-red-800 border-red-200 dark:bg-red-950/80 dark:text-red-300 dark:border-red-800",
};

export function AttendanceSimulator({
  subjects = [],
}: {
  subjects: SubjectAttendance[];
}) {
  const [selectedCode, setSelectedCode] = React.useState<string>(
    subjects[0]?.code || "EEE1001"
  );
  const [futureAttend, setFutureAttend] = React.useState<number>(0);
  const [futureMiss, setFutureMiss] = React.useState<number>(0);

  const selectedSubject = React.useMemo(() => {
    return (
      subjects.find((s) => s.code === selectedCode) || {
        code: "EEE1001",
        name: "Basic Electrical Engineering",
        classes_present: 42,
        classes_total: 52,
      }
    );
  }, [subjects, selectedCode]);

  const projectedMetrics = React.useMemo(() => {
    const present = selectedSubject.classes_present + futureAttend;
    const total = selectedSubject.classes_total + futureAttend + futureMiss;
    return calculateRisk(present, total);
  }, [selectedSubject, futureAttend, futureMiss]);

  return (
    <Card id="simulator" className="shadow-sm border">
      <CardHeader className="pb-3">
        <CardTitle className="text-xl sm:text-2xl flex items-center gap-2">
          <Calculator className="h-5 w-5 text-primary" aria-hidden="true" />
          Interactive Attendance Simulator
        </CardTitle>
        <CardDescription className="text-sm mt-1">
          Simulate what happens to your attendance percentage when you attend or miss upcoming classes.
        </CardDescription>
      </CardHeader>

      <CardContent className="pt-2 space-y-6">
        {/* Subject Selector */}
        <div>
          <label htmlFor="subject-select" className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            Select Subject:
          </label>
          <select
            id="subject-select"
            value={selectedCode}
            onChange={(e) => setSelectedCode(e.target.value)}
            className="mt-1.5 w-full rounded-lg border bg-background px-3 py-2 text-sm font-medium focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          >
            {subjects.map((s) => (
              <option key={s.code} value={s.code}>
                {s.code} — {s.name} ({s.classes_present}/{s.classes_total} attended)
              </option>
            ))}
          </select>
        </div>

        {/* Simulator Controls */}
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="rounded-xl border p-4 bg-green-50/30 dark:bg-green-950/20">
            <p className="text-xs font-semibold text-green-800 dark:text-green-300 uppercase">
              Attend Upcoming Classes (+1)
            </p>
            <div className="mt-3 flex items-center gap-3">
              <Button
                variant="outline"
                size="icon"
                onClick={() => setFutureAttend((prev) => Math.max(0, prev - 1))}
                aria-label="Decrease future attended classes"
                className="h-10 w-10 shrink-0"
              >
                <Minus className="h-4 w-4" />
              </Button>
              <span className="text-2xl font-bold w-12 text-center">{futureAttend}</span>
              <Button
                variant="outline"
                size="icon"
                onClick={() => setFutureAttend((prev) => prev + 1)}
                aria-label="Increase future attended classes"
                className="h-10 w-10 shrink-0"
              >
                <Plus className="h-4 w-4" />
              </Button>
            </div>
          </div>

          <div className="rounded-xl border p-4 bg-red-50/30 dark:bg-red-950/20">
            <p className="text-xs font-semibold text-red-800 dark:text-red-300 uppercase">
              Miss/Skip Upcoming Classes (+1)
            </p>
            <div className="mt-3 flex items-center gap-3">
              <Button
                variant="outline"
                size="icon"
                onClick={() => setFutureMiss((prev) => Math.max(0, prev - 1))}
                aria-label="Decrease future missed classes"
                className="h-10 w-10 shrink-0"
              >
                <Minus className="h-4 w-4" />
              </Button>
              <span className="text-2xl font-bold w-12 text-center">{futureMiss}</span>
              <Button
                variant="outline"
                size="icon"
                onClick={() => setFutureMiss((prev) => prev + 1)}
                aria-label="Increase future missed classes"
                className="h-10 w-10 shrink-0"
              >
                <Plus className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>

        {/* Projected Outcome Card */}
        <div className="rounded-xl border p-5 bg-card flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <p className="text-xs font-semibold text-muted-foreground uppercase">
              Projected Attendance Result
            </p>
            <div className="mt-1 flex items-baseline gap-3">
              <span className="text-3xl font-bold text-foreground">
                {projectedMetrics.current_pct}%
              </span>
              <Badge className={RISK_BADGE[projectedMetrics.risk_level]}>
                {projectedMetrics.risk_level}
              </Badge>
            </div>
            <p className="mt-2 text-xs text-muted-foreground">
              Total Classes: {selectedSubject.classes_present + futureAttend} / {selectedSubject.classes_total + futureAttend + futureMiss}
            </p>
          </div>

          <div className="text-left sm:text-right max-w-xs text-xs text-muted-foreground border-t sm:border-t-0 sm:border-l pt-3 sm:pt-0 sm:pl-4">
            <p>{projectedMetrics.projection}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
