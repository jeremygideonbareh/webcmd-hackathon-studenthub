import {
  Bot,
  BrainCircuit,
  Cpu,
  GraduationCap,
  ShieldCheck,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";

const STEPS = [
  {
    icon: GraduationCap,
    title: "1. Knowledge Pro Portal Sync",
    subtitle: "Christ University & Partner Portals",
    description:
      "WebCMD headless browser automation securely logs into your student portal, extracting real-time present and total class counts per subject.",
    badge: "WebCMD Automation",
  },
  {
    icon: Cpu,
    title: "2. Attendance Calculus & Simulator",
    subtitle: "Floor / Ceiling Attendance Math",
    description:
      "Deterministic math calculates exact consecutive classes you MUST attend or CAN skip to maintain your target 85% threshold.",
    badge: "Exact Calculus",
  },
  {
    icon: BrainCircuit,
    title: "3. Stream-Tailored AI Advisor",
    subtitle: "Engineering, Psychology, BBA, MBA",
    description:
      "Parses your resume against benchmark skills, recommending stream-specific portfolio projects and tailored action bullet points.",
    badge: "TF-IDF & NLP",
  },
  {
    icon: ShieldCheck,
    title: "4. SheerID & Student Perks",
    subtitle: "Discounts & Verified Scholarships",
    description:
      "Verifies your .edu student identity with SheerID to unlock GitHub Developer Pack, software licenses, and stream scholarships.",
    badge: "SheerID Verified",
  },
  {
    icon: Bot,
    title: "5. Self-Learning Preference Engine",
    subtitle: "Interactive Reaction Buttons",
    description:
      "React to job and housing cards with 👍👎⭐🚫 emojis. Atlas dynamically adjusts match weights in real-time.",
    badge: "Reinforcement Learning",
  },
];

export function HowItWorks() {
  return (
    <section id="how-it-works" aria-labelledby="how-it-works-heading" className="py-16 sm:py-20">
      <div className="mx-auto max-w-5xl">
        <div className="text-center mb-12">
          <Badge variant="outline" className="text-xs uppercase tracking-widest text-primary mb-3">
            Platform Architecture
          </Badge>
          <h2 id="how-it-works-heading" className="text-3xl font-bold tracking-tight sm:text-4xl">
            How Atlas Works
          </h2>
          <p className="mt-3 text-base text-muted-foreground max-w-2xl mx-auto">
            Atlas bridges your student portal, academic performance, career roadmap, and student perks into one unified operating dashboard.
          </p>
        </div>

        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {STEPS.map((step, idx) => (
            <Card key={idx} className="border shadow-sm bg-card hover:shadow-md transition-shadow">
              <CardContent className="p-6 space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-primary/10 text-primary">
                    <step.icon className="h-6 w-6" aria-hidden="true" />
                  </div>
                  <Badge variant="secondary" className="text-[10px] font-semibold">
                    {step.badge}
                  </Badge>
                </div>
                <div>
                  <h3 className="font-semibold text-lg leading-snug">{step.title}</h3>
                  <p className="text-xs font-medium text-primary mt-0.5">{step.subtitle}</p>
                  <p className="mt-2 text-xs text-muted-foreground leading-relaxed">
                    {step.description}
                  </p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}
