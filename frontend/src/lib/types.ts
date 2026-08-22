export type RiskLevel = "SAFE" | "CAUTION" | "WARNING" | "DANGER";
export type Reaction = "👍" | "👎" | "⭐" | "🚫";
export type StreamType = "Engineering" | "Psychology" | "BBA" | "MBA";

export interface SubjectAttendance {
  code: string;
  name: string;
  classes_present: number;
  classes_total: number;
  current_pct: number;
  classes_can_skip: number;
  classes_must_attend: number;
  risk_level: RiskLevel;
  projection: string;
}

export type AttendanceSubject = SubjectAttendance;

export interface FeedbackResponse {
  ok: boolean;
  weights: Record<string, number>;
}

export interface JobMatch {
  id: string;
  title: string;
  company: string;
  location?: string;
  stipend?: string;
  match_score: number;
  match_reason?: string;
  url?: string;
  category?: string;
}

export interface HousingListing {
  id: string;
  title: string;
  price: string;
  location?: string;
  url?: string;
  bedrooms?: number | string;
  furnished?: string;
}

export interface GpaInfo {
  student_id?: string;
  current_cgpa?: number;
  semester_gpa?: number;
  gpa_trend?: string;
}

export interface Scholarship {
  id: string;
  title: string;
  provider: string;
  amount: string;
  min_gpa: number;
  streams: string[];
  deadline: string;
  description: string;
  url: string;
}

export interface StudentDiscount {
  id: string;
  title: string;
  provider: string;
  category: string;
  discount: string;
  description: string;
  streams: string[];
  code?: string;
  url: string;
}

export interface AcademicDeadline {
  id: string;
  course: string;
  title: string;
  due_date: string;
  days_remaining: number;
  urgency: "HIGH" | "MEDIUM" | "LOW";
  type: "Assignment" | "Exam" | "Project" | "Lab";
}

export interface SkillGapAnalysis {
  stream: StreamType;
  readiness_score: number;
  matched_skills: string[];
  missing_critical_skills: string[];
  recommended_projects: {
    title: string;
    description: string;
    skills_gained: string[];
  }[];
  resume_bullet_suggestions: string[];
}

export interface Digest {
  attendance: SubjectAttendance[];
  jobs: JobMatch[];
  housing: HousingListing[];
  scholarships?: Scholarship[];
  discounts?: StudentDiscount[];
  deadlines?: AcademicDeadline[];
  gpa?: GpaInfo;
  weights?: Record<string, number>;
}
