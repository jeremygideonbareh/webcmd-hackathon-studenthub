# Atlas StudentHub — Orchestration Handoff

> **Living coordination document.** Read before every work session. Append session summaries after each commit.
> **Created:** 2026-08-22 by orchestration planner | **Updated:** 2026-08-22 (Major Feature Expansion & Work Division)
> **Status:** Integrated & Deployed — Live on Vercel (`webcmd-hackathon-studenthub.vercel.app`)

---

## 1. Project Snapshot

- **Project:** Atlas — StudentHub (WebCMD Hackathon 2026)
- **Repo:** `github.com/jeremygideonbareh/webcmd-hackathon-studenthub`
- **Language:** Python 3.10+ + JavaScript/TypeScript (React + WebCMD adapters)
- **Team:** Aaron (Portal), Sapna (Intelligence), Jeremy (Web delivery + root integration)
- **Current state:** Complete full-stack architecture with React + Vite + Tailwind dashboard, `WorkPageHero` GSAP kinetic hero, AI Resume & Skills Advisor (Engineering, Psychology, BBA, MBA), Scholarship Matcher, Student Deals Finder, Attendance Class Simulator, SheerID Student Verification, Supabase sync, Vercel deployment, and 47 passing unit tests.

---

## 2. Team Work Allocation & Responsibilities Matrix

| Teammate | Subsystem / Domain | Key Deliverables & Responsibilities | Clean Export Contracts |
|---|---|---|---|
| **Sapna** (Intelligence Architect) | `intelligence/` & `intel/` | 1. **AI Resume & Skills Advisor Engine** (`intelligence/advisor.py`) for **Engineering**, **Psychology**, **BBA**, and **MBA**.<br/>2. **Scholarship Aggregator & Matcher** (`intelligence/scholarships.py`).<br/>3. **Student Deals Catalog** (`intelligence/discounts.py`).<br/>4. **Resume Skills & TF-IDF Matcher** (`intel/parse_resume.py`, `intel/tfidf_matcher.py`). | `analyze_resume_skills(user_skills, stream)`<br/>`get_scholarships(gpa, stream)`<br/>`get_discounts(category, stream)`<br/>`get_matched_jobs(resume_data, category)` |
| **Aaron** (Portal Engineer) | `portal/` | 1. **WebCMD KP Portal Scraper** (`portal/webcmd_adapter.py`, `live_portal_scraper.py`).<br/>2. **Christ University CAPTCHA Solver & Credentials Adapter** (`ocr_solver.js`, `captcha_helper.js`).<br/>3. **Attendance & GPA Extractors** (`attendance_extractor.py`, `gpa_extractor.py`).<br/>4. **Attendance Calculus** (`portal/attendance_calculus.py`). | `get_attendance(config)`<br/>`get_gpa(config)`<br/>`simulate_attendance(present, total, attend, miss)` |
| **Jeremy** (Integration Commander) | `web/`, `frontend/`, `delivery/` | 1. **WorkPageHero Kinetic Hero** (`frontend/src/components/ui/work-page-hero.tsx`).<br/>2. **React + Tailwind Frontend Dashboard & Tabs** (`advisor-tab.tsx`, `scholarships-tab.tsx`, `discounts-tab.tsx`, `attendance-simulator.tsx`, `student-auth-modal.tsx`).<br/>3. **FastAPI & Vercel Endpoints** (`/api/digest`, `/api/advisor/analyze`, `/api/scholarships`, `/api/discounts`, `/api/attendance/simulate`).<br/>4. **Supabase Ledger & Pipeline Orchestration** (`orchestrator.py`, `supabase_store.py`). | Unified REST API & Vercel deployment |

---

## 3. Session Log

| Date | Who | What was done | What was learned |
|------|-----|---------------|------------------|
| 2026-08-22 | Orchestrator | Analyzed codebase, installed skills, created HANDOFF.md, produced phased plan | Project is greenfield. WebCMD skills available globally. |
| 2026-08-22 | Jeremy | **Pivot to website delivery** — FastAPI + vanilla JS replaces Discord. Updated plan, .env.example, requirements.txt. Scaffolded project + mock data. | JSON contracts made pivot cheap. |
| 2026-08-22 | Jeremy | **Phase 1-2 delivered on jeremy/delivery**: SQLite database.py + learning_engine.py (TDD, 18 tests), FastAPI dashboard, orchestrator.py pipeline. | Python 3.14 works with all deps. |
| 2026-08-22 | Jeremy | **Supabase backend + Vercel deploy live**: Supabase database + Vercel deployment. | Vercel GitHub push auto-deploy works seamlessly. |
| 2026-08-22 | Jeremy | **React + TypeScript frontend built** — Vite + React + shadcn UI, Tailwind, Recharts, GSAP, lucide-react. Math formulas verified against Aaron's attendance_calculus.py. | Vite `__dirname` warning fixed via `import.meta.dirname`. |
| 2026-08-22 | Jeremy | **UI Polish & Accessibility Completed**: 1) Touch target sizes (min 44px on mobile buttons/nav), 2) Accessibility (Skip link, ARIA labels, focus rings, WCAG AA risk badge colors), 3) Performance (`React.lazy` + `Suspense` code splitting), 4) Error Handling & Data Layer (`ErrorBoundary`, dashboard refresh/retry button). | `React.lazy` cleanly separates `dashboard` and `services` bundles. |
| 2026-08-22 | Jeremy | **Branch Integration & Test Pass**: Integrated Aaron's portal engine and Sapna's intel scraper into `main`. Added fallback handling in `portal/__init__.py`. 39/39 Python unit tests + 6/6 Vitest math tests passed. | Graceful fallback prevents CAPTCHA block from crashing backend pipeline. |
| 2026-08-22 | Jeremy | **Major Feature Expansion & WorkPageHero Landing Page**: 1) Integrated `WorkPageHero` GSAP kinetic scroll-expand hero component on frontend, 2) Built AI Resume & Skills Advisor (`intelligence/advisor.py`) for Engineering, Psychology, BBA, MBA, 3) Added Scholarship Aggregator & Student Deals catalog, 4) Built interactive Class Skip/Attend Simulator, 5) Added SheerID student verification & how-it-works platform explanation section, 6) 47/47 Python tests PASSED, 2.51s Vite build. Pushed live to GitHub main! | Stream-specific skill benchmarks give immediate value to non-engineering streams. |