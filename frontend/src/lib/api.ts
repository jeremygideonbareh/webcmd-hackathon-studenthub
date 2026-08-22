// Typed client for the live Atlas API (/api/digest, /api/feedback, /api/advisor, /api/scholarships, /api/discounts).

import type {
  Digest,
  FeedbackResponse,
  Reaction,
  Scholarship,
  SkillGapAnalysis,
  StreamType,
  StudentDiscount,
  SubjectAttendance,
} from "./types";

const DIGEST_URL = "/api/digest";
const FEEDBACK_URL = "/api/feedback";

export async function fetchDigest(): Promise<Digest> {
  const res = await fetch(DIGEST_URL);
  if (!res.ok) throw new Error(`/api/digest → ${res.status}`);
  return res.json() as Promise<Digest>;
}

export async function postFeedback(
  itemType: string,
  itemId: string,
  reaction: Reaction
): Promise<FeedbackResponse> {
  const res = await fetch(FEEDBACK_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      item_type: itemType,
      item_id: itemId,
      reaction,
    }),
  });
  if (!res.ok) throw new Error(`/api/feedback → ${res.status}`);
  return res.json() as Promise<FeedbackResponse>;
}

export async function analyzeSkills(
  skills: string[],
  stream: StreamType
): Promise<SkillGapAnalysis> {
  const res = await fetch("/api/advisor/analyze", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ skills, stream }),
  });
  if (!res.ok) throw new Error(`/api/advisor/analyze → ${res.status}`);
  return res.json() as Promise<SkillGapAnalysis>;
}

export async function fetchScholarships(
  gpa: number = 8.0,
  stream: StreamType = "Engineering"
): Promise<Scholarship[]> {
  const res = await fetch(`/api/scholarships?gpa=${gpa}&stream=${encodeURIComponent(stream)}`);
  if (!res.ok) throw new Error(`/api/scholarships → ${res.status}`);
  const data = await res.json();
  return data.scholarships || [];
}

export async function fetchDiscounts(
  category?: string,
  stream?: StreamType
): Promise<StudentDiscount[]> {
  const params = new URLSearchParams();
  if (category) params.append("category", category);
  if (stream) params.append("stream", stream);
  const res = await fetch(`/api/discounts?${params.toString()}`);
  if (!res.ok) throw new Error(`/api/discounts → ${res.status}`);
  const data = await res.json();
  return data.discounts || [];
}

export async function simulateAttendanceApi(
  present: number,
  total: number,
  futureAttend: number,
  futureMiss: number
): Promise<SubjectAttendance> {
  const res = await fetch("/api/attendance/simulate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      present,
      total,
      future_attend: futureAttend,
      future_miss: futureMiss,
    }),
  });
  if (!res.ok) throw new Error(`/api/attendance/simulate → ${res.status}`);
  return res.json() as Promise<SubjectAttendance>;
}
