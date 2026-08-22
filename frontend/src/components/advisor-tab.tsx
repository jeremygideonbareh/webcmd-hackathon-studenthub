import * as React from "react";
import {
  BookOpen,
  CheckCircle2,
  ChevronRight,
  ExternalLink,
  FileText,
  Lightbulb,
  Sparkles,
  XCircle,
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
import { analyzeSkills } from "@/lib/api";
import type { SkillGapAnalysis, StreamType } from "@/lib/types";

const STREAMS: StreamType[] = ["Engineering", "Psychology", "BBA", "MBA"];

export function AdvisorTab() {
  const [stream, setStream] = React.useState<StreamType>("Engineering");
  const [skillsInput, setSkillsInput] = React.useState("Python, Git, SQL, Data Structures");
  const [analysis, setAnalysis] = React.useState<SkillGapAnalysis | null>(null);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  const handleAnalyze = React.useCallback(async (selectedStream: StreamType, skillsText: string) => {
    setLoading(true);
    setError(null);
    try {
      const skillsArray = skillsText
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean);
      const res = await analyzeSkills(skillsArray, selectedStream);
      setAnalysis(res);
    } catch (err: any) {
      console.error("Failed to analyze skills:", err);
      setError(err?.message || "Failed to analyze skills. Please try again.");
    } finally {
      setLoading(false);
    }
  }, []);

  React.useEffect(() => {
    void handleAnalyze(stream, skillsInput);
  }, [stream, handleAnalyze]);

  return (
    <Card id="advisor" className="shadow-sm border">
      <CardHeader className="pb-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <CardTitle className="text-xl sm:text-2xl flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-primary" aria-hidden="true" />
              AI Skill & Resume Advisor
            </CardTitle>
            <CardDescription className="text-sm mt-1">
              Select your academic stream to discover missing skills, portfolio project ideas, and bullet point suggestions.
            </CardDescription>
          </div>
          <a
            href="https://resume-lab-one.vercel.app/"
            target="_blank"
            rel="noreferrer"
            className="inline-flex shrink-0 items-center gap-2 rounded-xl bg-gradient-to-r from-primary to-primary/80 px-4 py-2.5 text-xs font-bold text-primary-foreground shadow-md hover:opacity-95 transition-all"
          >
            <FileText className="h-4 w-4" />
            <span>Launch Resume Lab Analyzer</span>
            <ExternalLink className="h-3.5 w-3.5 opacity-80" />
          </a>
        </div>

        {/* Stream Pills */}
        <div className="mt-4 flex flex-wrap gap-2" role="tablist" aria-label="Academic streams">
          {STREAMS.map((s) => (
            <Button
              key={s}
              variant={stream === s ? "default" : "outline"}
              size="sm"
              onClick={() => setStream(s)}
              className="rounded-full px-4 text-xs font-semibold"
              role="tab"
              aria-selected={stream === s}
            >
              {s}
            </Button>
          ))}
        </div>
      </CardHeader>

      <CardContent className="space-y-6 pt-2">
        {/* Skills Input */}
        <div className="rounded-xl bg-muted/40 p-4 border">
          <label htmlFor="skills-input" className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            Your Current Skills (comma separated):
          </label>
          <div className="mt-2 flex flex-col sm:flex-row gap-2">
            <input
              id="skills-input"
              type="text"
              value={skillsInput}
              onChange={(e) => setSkillsInput(e.target.value)}
              placeholder="e.g. Python, SPSS, Excel, SQL, Financial Modeling"
              className="flex-1 rounded-lg border bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            />
            <Button
              size="sm"
              onClick={() => void handleAnalyze(stream, skillsInput)}
              disabled={loading}
              className="shrink-0 font-semibold"
            >
              {loading ? "Analyzing..." : "Analyze Profile"}
            </Button>
          </div>
        </div>

        {error && (
          <div className="rounded-xl border border-destructive/30 bg-destructive/5 p-4 text-sm text-destructive">
            <p className="font-semibold">Analysis Error</p>
            <p className="mt-1 text-xs text-muted-foreground">{error}</p>
            <Button
              variant="outline"
              size="sm"
              onClick={() => void handleAnalyze(stream, skillsInput)}
              className="mt-3 text-xs"
            >
              Retry Analysis
            </Button>
          </div>
        )}

        {loading && !analysis && (
          <div className="space-y-4 animate-pulse">
            <div className="h-24 rounded-xl bg-muted" />
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="h-32 rounded-xl bg-muted" />
              <div className="h-32 rounded-xl bg-muted" />
            </div>
          </div>
        )}

        {analysis && (
          <div className="space-y-6">
            {/* Readiness Score */}
            <div className="flex flex-wrap items-center justify-between gap-4 rounded-xl border bg-card p-5">
              <div>
                <p className="text-xs font-semibold text-muted-foreground uppercase">
                  {analysis.stream} Career Readiness
                </p>
                <p className="mt-1 text-3xl font-bold text-primary">
                  {analysis.readiness_score}%
                </p>
              </div>
              <div className="max-w-xs text-xs text-muted-foreground">
                <p>Based on core competency benchmarks for {analysis.stream} internships & entry-level roles.</p>
              </div>
            </div>

            {/* Matched vs Missing Skills */}
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="rounded-xl border p-4 bg-green-50/40 dark:bg-green-950/20">
                <div className="flex items-center gap-2 font-semibold text-green-700 dark:text-green-300 text-sm">
                  <CheckCircle2 className="h-4 w-4" aria-hidden="true" />
                  Matched Skills ({analysis.matched_skills.length})
                </div>
                <div className="mt-3 flex flex-wrap gap-1.5">
                  {analysis.matched_skills.length === 0 ? (
                    <span className="text-xs text-muted-foreground">No benchmark skills matched yet.</span>
                  ) : (
                    analysis.matched_skills.map((skill) => (
                      <Badge key={skill} variant="secondary" className="bg-green-100 dark:bg-green-900/40 text-green-800 dark:text-green-300 text-xs">
                        {skill}
                      </Badge>
                    ))
                  )}
                </div>
              </div>

              <div className="rounded-xl border p-4 bg-amber-50/40 dark:bg-amber-950/20">
                <div className="flex items-center gap-2 font-semibold text-amber-700 dark:text-amber-300 text-sm">
                  <XCircle className="h-4 w-4" aria-hidden="true" />
                  Recommended Skills to Learn ({analysis.missing_critical_skills.length})
                </div>
                <div className="mt-3 flex flex-wrap gap-1.5">
                  {analysis.missing_critical_skills.map((skill) => (
                    <Badge key={skill} variant="outline" className="border-amber-300 dark:border-amber-800 text-amber-800 dark:text-amber-300 text-xs">
                      + {skill}
                    </Badge>
                  ))}
                </div>
              </div>
            </div>

            {/* Recommended Stream Projects */}
            <div>
              <h4 className="text-sm font-semibold flex items-center gap-2 mb-3">
                <Lightbulb className="h-4 w-4 text-primary" aria-hidden="true" />
                Recommended Portfolio Projects for {analysis.stream}
              </h4>
              <div className="grid gap-3 sm:grid-cols-2">
                {analysis.recommended_projects.map((proj) => (
                  <div key={proj.title} className="rounded-xl border p-4 bg-card">
                    <p className="font-semibold text-sm">{proj.title}</p>
                    <p className="mt-1 text-xs text-muted-foreground leading-relaxed">
                      {proj.description}
                    </p>
                    <div className="mt-3 flex flex-wrap gap-1">
                      {proj.skills_gained.map((sg) => (
                        <span key={sg} className="rounded bg-muted px-2 py-0.5 text-[10px] font-medium">
                          {sg}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Resume Bullet Suggestions */}
            <div>
              <h4 className="text-sm font-semibold flex items-center gap-2 mb-3">
                <BookOpen className="h-4 w-4 text-primary" aria-hidden="true" />
                Tailored Resume Action Bullets
              </h4>
              <div className="space-y-2">
                {analysis.resume_bullet_suggestions.map((bullet, idx) => (
                  <div key={idx} className="flex items-start gap-2.5 rounded-lg border bg-muted/20 p-3 text-xs leading-relaxed text-foreground">
                    <ChevronRight className="h-4 w-4 text-primary shrink-0 mt-0.5" aria-hidden="true" />
                    <span>{bullet}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
