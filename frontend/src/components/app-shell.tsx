import * as React from "react";
import {
  Award,
  BookOpen,
  Briefcase,
  Calculator,
  ChevronDown,
  GraduationCap,
  Home,
  Menu,
  Percent,
  Sparkles,
  X,
} from "lucide-react";

import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Separator } from "@/components/ui/separator";
import { cn } from "@/lib/utils";

const NAV = [
  { href: "#home", label: "Overview", icon: Home },
  { href: "#attendance", label: "Attendance Risk", icon: GraduationCap },
  { href: "#simulator", label: "Class Simulator", icon: Calculator },
  { href: "#advisor", label: "AI Skill Advisor", icon: Sparkles },
  { href: "#jobs", label: "Internships", icon: Briefcase },
  { href: "#scholarships", label: "Scholarships", icon: Award },
  { href: "#discounts", label: "Student Deals", icon: Percent },
  { href: "#housing", label: "Housing", icon: Home },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const [open, setOpen] = React.useState(false);

  React.useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape" && open) {
        setOpen(false);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [open]);

  return (
    <div className="min-h-screen bg-background">
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-50 focus:rounded-md focus:bg-primary focus:px-4 focus:py-2 focus:text-primary-foreground focus:shadow-lg focus:outline-none focus:ring-2 focus:ring-ring"
      >
        Skip to main content
      </a>

      {/* Sidebar — desktop */}
      <aside className="fixed inset-y-0 left-0 z-30 hidden w-64 flex-col border-r bg-card md:flex">
        <SidebarContent />
      </aside>

      {/* Sidebar — mobile drawer */}
      {open && (
        <div
          className="fixed inset-0 z-40 md:hidden"
          role="dialog"
          aria-modal="true"
          aria-label="Navigation drawer"
        >
          <div
            className="absolute inset-0 bg-black/50 backdrop-blur-sm transition-opacity"
            onClick={() => setOpen(false)}
            aria-hidden="true"
          />
          <aside className="absolute inset-y-0 left-0 flex w-72 flex-col border-r bg-card pb-[env(safe-area-inset-bottom)] shadow-2xl">
            <div className="flex items-center justify-between p-4">
              <Brand />
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setOpen(false)}
                aria-label="Close navigation menu"
                className="h-11 w-11 rounded-lg"
              >
                <X className="h-5 w-5" aria-hidden="true" />
              </Button>
            </div>
            <Separator />
            <SidebarContent onNavigate={() => setOpen(false)} />
          </aside>
        </div>
      )}

      {/* Mobile top bar */}
      <header className="sticky top-0 z-20 flex items-center justify-between border-b bg-card/95 px-4 py-3 backdrop-blur md:hidden">
        <Brand />
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setOpen(true)}
          aria-label="Open navigation menu"
          aria-expanded={open}
          className="h-11 w-11 rounded-lg"
        >
          <Menu className="h-5 w-5" aria-hidden="true" />
        </Button>
      </header>

      <div className="md:pl-64">
        <main id="main-content" className="mx-auto max-w-6xl px-4 py-6 sm:px-6 lg:px-8">
          {children}
        </main>
      </div>
    </div>
  );
}

function Brand() {
  return (
    <div className="flex items-center gap-2.5">
      <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-primary text-primary-foreground shadow-sm">
        <BookOpen className="h-5 w-5" aria-hidden="true" />
      </div>
      <span className="text-xl font-bold tracking-tight">Atlas</span>
    </div>
  );
}

function SidebarContent({ onNavigate }: { onNavigate?: () => void }) {
  return (
    <>
      <div className="p-4">
        <Brand />
      </div>
      <Separator />
      <nav aria-label="Main Navigation" className="flex-1 space-y-1 p-2 overflow-y-auto">
        {NAV.map((item) => (
          <a
            key={item.href}
            href={item.href}
            onClick={onNavigate}
            className={cn(
              "flex min-h-[44px] items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            )}
          >
            <item.icon className="h-4 w-4 shrink-0" aria-hidden="true" />
            {item.label}
          </a>
        ))}
      </nav>
      <Separator />
      <div className="p-4">
        <ProfileMenu />
      </div>
    </>
  );
}

function ProfileMenu() {
  return (
    <Collapsible>
      <CollapsibleTrigger asChild>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="ghost"
              className="min-h-[44px] w-full justify-start gap-2 px-2 focus-visible:ring-2 focus-visible:ring-ring"
              aria-label="Student account menu"
            >
              <Avatar className="h-8 w-8">
                <AvatarFallback className="bg-primary/10 text-primary font-semibold">ST</AvatarFallback>
              </Avatar>
              <span className="flex-1 text-left text-sm font-medium">
                Student Portal
              </span>
              <ChevronDown className="h-4 w-4 text-muted-foreground" aria-hidden="true" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="start" className="w-56">
            <DropdownMenuLabel>My Account</DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem>Profile & Stream</DropdownMenuItem>
            <DropdownMenuItem>Preferences</DropdownMenuItem>
            <DropdownMenuItem>Portal Credentials</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </CollapsibleTrigger>
      <CollapsibleContent className="space-y-1 px-2 pt-1">
        <a
          href="#attendance"
          className="flex min-h-[36px] items-center rounded-md px-3 py-1.5 text-xs text-muted-foreground hover:bg-accent hover:text-foreground"
        >
          Risk report
        </a>
        <a
          href="#advisor"
          className="flex min-h-[36px] items-center rounded-md px-3 py-1.5 text-xs text-muted-foreground hover:bg-accent hover:text-foreground"
        >
          Skill recommendations
        </a>
      </CollapsibleContent>
    </Collapsible>
  );
}
