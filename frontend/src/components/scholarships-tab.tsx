import * as React from "react";
import { Award, Calendar, ExternalLink, GraduationCap } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { fetchScholarships } from "@/lib/api";
import type { Scholarship, StreamType } from "@/lib/types";

const STREAMS: StreamType[] = ["Engineering", "Psychology", "BBA", "MBA"];

export function ScholarshipsTab({
  initialScholarships = [],
}: {
  initialScholarships?: Scholarship[];
}) {
  const [scholarships, setScholarships] = React.useState<Scholarship[]>(initialScholarships);
  const [stream, setStream] = React.useState<StreamType | "All">("All");

  React.useEffect(() => {
    if (initialScholarships.length > 0 && stream === "All") {
      setScholarships(initialScholarships);
      return;
    }
    const filterStream = stream === "All" ? "Engineering" : stream;
    fetchScholarships(7.5, filterStream)
      .then((data) => setScholarships(data))
      .catch((err) => console.error("Error loading scholarships:", err));
  }, [stream, initialScholarships]);

  return (
    <Card id="scholarships" className="shadow-sm border">
      <CardHeader className="flex flex-row items-center justify-between pb-3">
        <div>
          <CardTitle className="text-xl sm:text-2xl flex items-center gap-2">
            <Award className="h-5 w-5 text-primary" aria-hidden="true" />
            Scholarships & Grants
          </CardTitle>
          <CardDescription className="text-sm mt-1">
            Verified financial aid opportunities tailored to your stream and GPA eligibility.
          </CardDescription>
        </div>

        {/* Stream Filter */}
        <div className="flex flex-wrap gap-1.5" role="tablist" aria-label="Scholarship stream filter">
          <Button
            variant={stream === "All" ? "default" : "outline"}
            size="sm"
            onClick={() => setStream("All")}
            className="rounded-full text-xs"
          >
            All
          </Button>
          {STREAMS.map((s) => (
            <Button
              key={s}
              variant={stream === s ? "default" : "outline"}
              size="sm"
              onClick={() => setStream(s)}
              className="rounded-full text-xs"
            >
              {s}
            </Button>
          ))}
        </div>
      </CardHeader>

      <CardContent className="pt-2 space-y-4">
        {scholarships.length === 0 ? (
          <div className="py-12 text-center text-muted-foreground">
            <GraduationCap className="h-10 w-10 mx-auto mb-2 opacity-50" aria-hidden="true" />
            <p className="text-sm font-medium">No active scholarships matching this filter.</p>
          </div>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2">
            {scholarships.map((s) => (
              <article key={s.id} className="flex flex-col justify-between rounded-xl border p-4 sm:p-5 bg-card hover:shadow-sm transition-shadow">
                <div>
                  <div className="flex items-start justify-between gap-2">
                    <h4 className="font-semibold text-base leading-snug text-foreground">{s.title}</h4>
                    <Badge variant="secondary" className="shrink-0 text-xs font-bold text-primary bg-primary/10">
                      {s.amount}
                    </Badge>
                  </div>
                  <p className="mt-1 text-xs font-medium text-muted-foreground">{s.provider}</p>
                  <p className="mt-2 text-xs text-muted-foreground leading-relaxed">{s.description}</p>

                  <div className="mt-3 flex flex-wrap gap-2 text-xs">
                    <span className="rounded bg-muted px-2 py-0.5 font-medium">
                      Min GPA: <strong>{s.min_gpa}</strong>
                    </span>
                    <span className="flex items-center gap-1 rounded bg-muted px-2 py-0.5 font-medium text-muted-foreground">
                      <Calendar className="h-3 w-3" aria-hidden="true" />
                      Deadline: {s.deadline}
                    </span>
                  </div>
                </div>

                <div className="mt-4 border-t pt-3 flex items-center justify-between">
                  <div className="flex flex-wrap gap-1">
                    {s.streams.map((st) => (
                      <Badge key={st} variant="outline" className="text-[10px]">
                        {st}
                      </Badge>
                    ))}
                  </div>
                  {s.url && (
                    <a
                      href={s.url}
                      target="_blank"
                      rel="noreferrer"
                      className="inline-flex min-h-[44px] items-center gap-1 text-xs font-semibold text-primary hover:underline"
                    >
                      Apply Now <ExternalLink className="h-3 w-3" aria-hidden="true" />
                    </a>
                  )}
                </div>
              </article>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
