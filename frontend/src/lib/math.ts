// Attendance calculus — port of portal/attendance_calculus.py.
// Real math, no mock data.

import type { AttendanceSubject, RiskLevel } from "./types";

export interface RiskResult {
  current_pct: number;
  classes_present: number;
  classes_total: number;
  classes_can_skip: number;
  classes_must_attend: number;
  risk_level: RiskLevel;
  projection: string;
}

/**
 * Compute attendance risk for a single subject.
 *
 * can_skip    = floor((P - θ·T) / θ)      when P/T >= θ, else 0
 * must_attend = ceil((θ·T - P) / (1 - θ))  when P/T <  θ, else 0
 *
 * where P = classes present, T = classes total, θ = threshold (default 0.85).
 * Risk bands: >=90 SAFE, >=85 CAUTION, >=80 WARNING, <80 DANGER.
 */
export function calculateRisk(
  present: number,
  total: number,
  threshold = 0.85
): RiskResult {
  const pct = total > 0 ? (present / total) * 100 : 0;

  let canSkip = 0;
  let mustAttend = 0;

  if (pct >= threshold * 100) {
    canSkip = Math.floor((present - threshold * total) / threshold);
  } else {
    mustAttend = Math.ceil((threshold * total - present) / (1 - threshold));
  }

  let risk: RiskLevel;
  if (pct >= 90) risk = "SAFE";
  else if (pct >= 85) risk = "CAUTION";
  else if (pct >= 80) risk = "WARNING";
  else risk = "DANGER";

  const projection = buildProjection(risk, canSkip, mustAttend, pct);

  return {
    current_pct: round2(pct),
    classes_present: present,
    classes_total: total,
    classes_can_skip: Math.max(0, canSkip),
    classes_must_attend: Math.max(0, mustAttend),
    risk_level: risk,
    projection,
  };
}

function buildProjection(
  risk: RiskLevel,
  canSkip: number,
  mustAttend: number,
  pct: number
): string {
  const p = round2(pct);
  switch (risk) {
    case "SAFE":
      return `You're at ${p}%. You can safely skip ${canSkip} more classes.`;
    case "CAUTION":
      return `You're at ${p}%. You can skip ${canSkip} class(es) but be careful.`;
    case "WARNING":
      return `You're at ${p}%. Must attend next ${mustAttend} classes to hit 85%.`;
    default:
      return `DANGER: ${p}%. Must attend ${mustAttend} consecutive classes immediately!`;
  }
}

function round2(n: number): number {
  return Math.round(n * 100) / 100;
}

/**
 * Recompute risk fields for a subject using raw P/T values. Useful when the
 * backend already supplied the values (verify) or when thresholds change.
 */
export function recomputeSubject(
  s: AttendanceSubject,
  threshold = 0.85
): AttendanceSubject {
  const r = calculateRisk(s.classes_present, s.classes_total, threshold);
  return { ...s, ...r };
}
