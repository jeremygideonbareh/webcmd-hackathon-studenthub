// Types matching the Atlas digest contract (data/*.json + /api/digest).

export type RiskLevel = "SAFE" | "CAUTION" | "WARNING" | "DANGER" | string;

export interface AttendanceSubject {
  code: string;
  name: string;
  current_pct: number;
  classes_present: number;
  classes_total: number;
  classes_can_skip: number;
  classes_must_attend: number;
  projection: string;
  risk_level: RiskLevel;
}

export interface Gpa {
  student_id?: string;
  current_cgpa?: number;
  semester_gpa?: number;
  scraped_at?: string;
  gpa_trend?: string;
}

export interface Job {
  id: string;
  title: string;
  company: string;
  match_score: number;
  match_reason: string;
  stipend?: string;
  location?: string;
  url?: string;
  category?: string;
  image_url?: string | null;
  skills_required?: string[];
}

export interface HousingListing {
  id: string;
  title: string;
  price: string;
  location?: string;
  url?: string;
  bedrooms?: number;
  furnished?: string;
}

export interface Digest {
  attendance: AttendanceSubject[];
  jobs: Job[];
  housing: HousingListing[];
  gpa: Gpa;
  weights: Record<string, number>;
}

export type Reaction = "👍" | "👎" | "⭐" | "🚫";

export interface FeedbackResponse {
  ok: boolean;
  weights: Record<string, number>;
  error?: string;
}
