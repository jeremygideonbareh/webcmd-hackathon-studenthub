# Atlas StudentHub — Orchestration Handoff

> **Living coordination document.** Read before every work session. Append session summaries after each commit.
> **Created:** 2026-08-22 by orchestration planner | **Updated:** 2026-08-22 (website pivot — delivery is now a **FastAPI web app**, not Discord)
> **Status:** Greenfield — scaffold + mock data landed on `main`; delivery layer being built by Jeremy

---

## 1. Project Snapshot

- **Project:** Atlas — StudentHub (WebCMD Hackathon 2026)
- **Repo:** `github.com/jeremygideonbareh/webcmd-hackathon-studenthub`
- **Language:** Python 3.10+ + JavaScript (WebCMD adapters)
- **Team:** Aaron (Portal), Sapna (Intelligence), Jeremy (Web delivery + root)
- **Current state:** Scaffold, config, mock data, and docs on `main`. Delivery (`web/` + `delivery/`) in progress. Portal branch `aaron/portal` exists on origin.
- **Full plan:** See `IMPLEMENTATION_PLAN.md` for architecture, data schemas, module specs, timeline.

### Delivery Architecture (post-pivot)

```
Aaron (unchanged)        Sapna (unchanged)          Jeremy (delivery)
KP portal → JSON      →  resume/jobs/housing →   ┌─ web/app.py (FastAPI)
attendance/gpa           matcher + GPA filter    ├─ dashboard (static/, vanilla JS)
        │                       │               ├─ POST /api/feedback (👍👎⭐🚫)
        └────── data/*.json ────┘               ├─ learning_engine.py (weight updates)
                                                 ├─ database.py (SQLite)
                                                 └─ orchestrator.py (pipeline)
```

- Discord webhook/bot **cancelled**. Optional `delivery/notify_discord.py` bonus only.
- Learning loop now driven by buttons on the dashboard (same multipliers, same SQLite).

### Data Contracts (module interfaces — DO NOT change without notifying team)

| Contract | Producer to Consumer | File |
|----------|---------------------|------|
| attendance.json | Aaron to Jeremy | data/attendance.json |
| risk_report.json | Aaron to Jeremy | data/risk_report.json |
| gpa.json | Aaron to Sapna + Jeremy | data/gpa.json |
| filtered_jobs.json | Sapna to Jeremy | data/filtered_jobs.json |
| housing_raw.json | Sapna to Jeremy | data/housing_raw.json |
| preference_weights | Jeremy SQLite to Sapna matcher | in-memory dict |

> **Sapna (optional):** include `image_url` on job listings in `filtered_jobs.json` if easily available — the dashboard renders it. Skip if rushed.

Full JSON schemas: `IMPLEMENTATION_PLAN.md` section Shared Contracts.

---

## 2. Skills Inventory

### Project skills (`.agents/skills/` + `.claude/skills/`)

| Skill | Used By | Purpose |
|-------|---------|---------|
| pytest | All | Test structure, fixtures, parametrize, coverage |
| scikit-learn | Sapna | TF-IDF vectorization, cosine similarity |
| web-scraping-python | Sapna | requests/curl_cffi/BeautifulSoup patterns, anti-bot |
| machine-learning | Sapna | General ML/NLP guidance for matching engine |
| discord-bot | (unused post-pivot) | Kept only if optional webhook bonus is built |

### Pre-installed global skills (already available)

| Skill | Used By | Purpose |
|-------|---------|---------|
| webcmd-usage | Aaron | Top-level map of WebCMD CLI capabilities |
| webcmd-adapter-author | Aaron | Guide for writing deterministic WebCMD adapters |
| webcmd-autofix | Aaron | Auto-fix broken WebCMD adapters |
| webcmd-browser | Aaron | Ad-hoc Playwright interaction for KP portal |
| webdev / frontend-design | Jeremy | Full-stack web development, UI quality |
| web-perf / vercel-react-best-practices | Jeremy | Frontend performance |
| dispatching-parallel-agents | Coordinator | Orchestrate 3-person parallel work |
| test-driven-development | All | TDD: RED then GREEN then REFACTOR |
| systematic-debugging | All | Root-cause analysis for bugs |
| verification-before-completion | All | Evidence-based completion claims |
| security-best-practices | All | Credential handling, token safety, scraping ethics |

---

## 3. Agent Assignment Matrix

| Agent | Assigned To | When to Invoke |
|-------|-------------|----------------|
| planner | Coordinator (done) | Complex features, refactoring |
| architect | Coordinator (done) | Data contracts in IMPLEMENTATION_PLAN.md |
| tdd-guide | ALL team members | Before writing any module |
| python-reviewer | ALL modules before merge | After writing/modifying code |
| security-reviewer | Jeremy (creds), Aaron (auth), Sapna (scraping) | Before commits, sensitive code |
| build-error-resolver | ALL | When pip install / import fails |
| e2e-runner | Jeremy | Full pipeline test (Checkpoint 4) |
| refactor-cleaner | ALL | Phase 4 code maintenance |
| doc-updater | Jeremy | Update READMEs per subsystem |

---

## 4. Implementation Plan — Phased Subtask Breakdown

Legend: `[TDD]` = test first | `[BLOCKER]` = others cannot proceed | `[PARALLEL]` = concurrent

### Phase 0: Scaffolding and Mock Data (Jeremy — CRITICAL PATH)

> Aaron and Sapna CANNOT start until this is on `main`.

| # | Subtask | File(s) | Agent/Skill | Deps |
|---|---------|---------|-------------|------|
| 0.1 | Create dirs: portal/, intelligence/, delivery/, web/static/, data/mock/, tests/ | dirs | — | — |
| 0.2 | Create __init__.py for portal/, intelligence/, delivery/ | 3 files | — | 0.1 |
| 0.3 | Create config.py — loads .env + config.yaml, exposes Config dataclass | config.py | security-reviewer | 0.1 |
| 0.4 | Create config.yaml — threshold 85, GPA thresholds, KP URL, scraper settings | config.yaml | — | 0.3 |
| 0.5 | **[BLOCKER]** Create ALL mock data files matching every contract | data/mock/*.json (7 files) | — | 0.1 |
| 0.6 | Create data/sample_resume.tex — realistic LaTeX resume | data/sample_resume.tex | — | 0.1 |
| 0.7 | Commit + push scaffolding to main, notify team | git | — | 0.1-0.6 |

Verification gate: fresh `git pull` produces full tree. Mock JSON validates against IMPLEMENTATION_PLAN.md schemas.

### Phase 1: Foundation Modules (ALL 3 IN PARALLEL after Phase 0)

#### Aaron — Portal Foundation (branch aaron/portal)

| # | Subtask | File(s) | Agent/Skill | Deps |
|---|---------|---------|-------------|------|
| A1.1 | **[TDD]** Test calculate_risk() — SAFE/CAUTION/WARNING/DANGER, edge cases | tests/test_calculus.py | tdd-guide, pytest | 0.7 |
| A1.2 | Implement attendance_calculus.py — floor/ceiling math, projection messages | portal/attendance_calculus.py | python-reviewer | A1.1 |
| A1.3 | Verify: pytest tests/test_calculus.py -v | — | verification | A1.2 |
| A1.4 | Install WebCMD: npm i -g @agentrhq/webcmd, webcmd doctor | — | webcmd-usage | 0.7 |
| A1.5 | Create session: webcmd --profile kp_student session create -f json | — | webcmd-usage | A1.4 |

#### Sapna — Intelligence Foundation (branch sapna/intel)

| # | Subtask | File(s) | Agent/Skill | Deps |
|---|---------|---------|-------------|------|
| S1.1 | **[TDD]** Test JobMatcher.match() — cosine, skill overlap, prefs, tech-term preservation | tests/test_matcher.py | tdd-guide, pytest, scikit-learn | 0.7 |
| S1.2 | Implement matcher.py — TF-IDF, cosine sim, skill overlap, preference scoring, explainability | intelligence/matcher.py | python-reviewer, scikit-learn | S1.1 |
| S1.3 | Verify: pytest tests/test_matcher.py -v | — | verification | S1.2 |

#### Jeremy — Delivery Foundation (branch jeremy/delivery)

| # | Subtask | File(s) | Agent/Skill | Deps |
|---|---------|---------|-------------|------|
| J1.1 | **[TDD]** Test Database CRUD — log_reaction, get/update_weight, get_all_weights, log_digest | tests/test_database.py | tdd-guide, pytest | 0.7 |
| J1.2 | Implement database.py — SQLite schema (3 tables), all CRUD methods | delivery/database.py | python-reviewer, security-reviewer | J1.1 |
| J1.3 | **[TDD]** Test LearningEngine — each emoji multiplier, clamping, category extraction | tests/test_learning_engine.py | tdd-guide, pytest | J1.2 |
| J1.4 | Implement learning_engine.py — process_reaction(), emoji to weight, clamp [0.1, 3.0] | delivery/learning_engine.py | python-reviewer | J1.3 |
| J1.5 | Verify: pytest tests/test_database.py tests/test_learning_engine.py -v | — | verification | J1.2, J1.4 |

### Phase 2: Core Implementation (ALL 3 IN PARALLEL)

#### Aaron — Portal Core

| # | Subtask | File(s) | Agent/Skill | Deps |
|---|---------|---------|-------------|------|
| A2.1 | Study KP portal login form HTML structure | — | webcmd-browser, agent-browser | A1.5 |
| A2.2 | Write WebCMD adapter kp_attendance_adapter.js — login, navigate, extract table, logout | portal/adapters/kp_attendance_adapter.js | webcmd-adapter-author | A2.1 |
| A2.3 | Implement webcmd_adapter.py — subprocess wrapper (see NOTE), scrape_attendance() | portal/webcmd_adapter.py | python-reviewer | A2.2 |
| A2.4 | Implement attendance_extractor.py — parse WebCMD output, colspan/rowspan, map to contract | portal/attendance_extractor.py | python-reviewer | A2.3 |
| A2.5 | Write kp_gpa_adapter.js — navigate grades page, extract CGPA/SGPA | portal/adapters/kp_gpa_adapter.js | webcmd-adapter-author | A2.2 |
| A2.6 | Implement gpa_extractor.py — CGPA/SGPA, GPA trend detection | portal/gpa_extractor.py | python-reviewer | A2.5 |
| A2.7 | Implement kp_scraper.py — session mgmt, JSESSIONID expiry, re-auth, 15-min lockout prevention | portal/kp_scraper.py | security-reviewer, systematic-debugging | A2.3, A2.6 |
| A2.8 | Create portal/__init__.py API: get_attendance(), get_gpa(), get_risk_report() | portal/__init__.py | — | A2.4, A2.6, A2.7 |
| A2.9 | Test portal API output matches mock schema | tests/test_portal_api.py | verification | A2.8 |

> **NOTE (A2.3) — WebCMD CLI corrections verified 2026-08-22:**
> 1. `session create` has NO `--profile` flag. Use root flag: `webcmd --profile <name> session create -f json`.
> 2. `browser run` has NO `-f json` flag. Do NOT append it; parse the program's returned output.
> 3. Raw `browser run` requires a root `--session <id>` (SESSION_REQUIRED otherwise). Create a session, hold the ID, and call `webcmd --profile <name> --session <id> browser run --file <path>`.

#### Sapna — Intelligence Core

| # | Subtask | File(s) | Agent/Skill | Deps |
|---|---------|---------|-------------|------|
| S2.1 | **[TDD]** Test parse_resume() — LaTeX stripping, section extraction, skill parsing | tests/test_resume_parser.py | tdd-guide, pytest | 0.7 |
| S2.2 | Implement resume_parser.py — pylatexenc + regex fallback, returns resume_profile.json | intelligence/resume_parser.py | python-reviewer | S2.1 |
| S2.3 | Implement job_scraper.py — scrape_internshala() curl_cffi + scrape_github_internships() | intelligence/job_scraper.py | web-scraping-python, security-reviewer | S1.2 |
| S2.4 | Implement housing_scraper.py — scrape_nobroker() REST API | intelligence/housing_scraper.py | web-scraping-python | S2.3 |
| S2.5 | Implement gpa_filter.py — GPAFilter, competitive/balanced/portfolio modes, weight application | intelligence/gpa_filter.py | python-reviewer | S1.2 |
| S2.6 | **[TDD]** Test GPAFilter.filter_jobs() — all 3 modes, weight application, edge cases | tests/test_gpa_filter.py | tdd-guide, pytest | S2.5 |
| S2.7 | Create intelligence/__init__.py API: get_matched_jobs(gpa, weights), get_housing() | intelligence/__init__.py | — | S2.2, S2.3, S2.4, S2.5 |
| S2.8 | Integration test: resume to match to filter to filtered_jobs.json contract | tests/test_intel_pipeline.py | verification | S2.7 |

#### Jeremy — Web Delivery Core

| # | Subtask | File(s) | Agent/Skill | Deps |
|---|---------|---------|-------------|------|
| J2.1 | Implement orchestrator.py — CLI modes `--mock` / `--live` / `--live-demo`; runs pipeline, writes data/*.json | orchestrator.py | python-reviewer | J1.2, J1.4 |
| J2.2 | Implement web/app.py — FastAPI: GET / (dashboard), GET /api/digest, POST /api/feedback | web/app.py | python-reviewer, webdev | J1.2, J1.4 |
| J2.3 | Implement dashboard — static/index.html, app.js, style.css (attendance, jobs w/ reaction buttons, housing) | web/static/* | frontend-design | J2.2 |
| J2.4 | Test web API: pytest tests/test_web_api.py — /api/digest shape, /api/feedback writes SQLite | tests/test_web_api.py | tdd-guide, pytest | J2.2 |
| J2.5 | Checkpoint 2: run orchestrator --mock, start server, dashboard shows mock digest live | — | verification, e2e-runner | J2.3 |
| J2.6 | (Bonus) delivery/notify_discord.py — fires webhook only if DISCORD_WEBHOOK_URL set | delivery/notify_discord.py | python-reviewer | J2.1 |

### Phase 3: Integration (CHECKPOINT 3 — MAJOR, highest risk)

| # | Subtask | Owner | Agent/Skill | Deps |
|---|---------|-------|-------------|------|
| I3.1 | Merge aaron/portal to main | Jeremy | finishing-a-development-branch | A2.9, S2.8, J2.5 |
| I3.2 | Merge sapna/intel to main | Jeremy | finishing-a-development-branch | I3.1 |
| I3.3 | Merge jeremy/delivery to main | Jeremy | finishing-a-development-branch | I3.2 |
| I3.4 | Resolve merge conflicts (config.py, requirements.txt) | Jeremy | build-error-resolver | I3.3 |
| I3.5 | Run full test suite: pytest tests/ -v (ALL pass) | Jeremy | verification, e2e-runner | I3.4 |
| I3.6 | Wire real modules into orchestrator.py (replace mock loads) | Jeremy | python-reviewer | I3.5 |
| I3.7 | Wire preference_weights feedback loop (SQLite to matcher) | Jeremy | python-reviewer | I3.6 |
| I3.8 | Wire GPA to InternRadar loop (detect GPA drop, switch mode) | Jeremy | architect | I3.7 |
| I3.9 | Code review of merged main (all modules) | Coordinator | python-reviewer, security-reviewer | I3.8 |
| I3.10 | End-to-end test with real data (Checkpoint 4) | All | e2e-runner | I3.9 |

### Phase 4: Polish and Demo (Hours 9-10)

| # | Subtask | Owner | Agent/Skill | Deps |
|---|---------|-------|-------------|------|
| P4.1 | Fix any integration bugs from Checkpoint 3/4 | All | systematic-debugging | I3.10 |
| P4.2 | Add match score explanations to job cards | Sapna | — | I3.10 |
| P4.3 | Polish attendance alert cards | Aaron | — | I3.10 |
| P4.4 | Final dashboard polish + digest layout | Jeremy | frontend-design | P4.2, P4.3 |
| P4.5 | Code freeze. Write portal/README.md, intelligence/README.md, web/README.md | Aaron, Sapna, Jeremy | doc-updater | P4.4 |
| P4.6 | Final merge to main, demo rehearsal | Jeremy | — | P4.5 |

---

## 5. Dependency Graph (critical path)

```
Phase 0 (Jeremy scaffold + mock)
  |
  +---> Phase 1 (parallel: Aaron calculus, Sapna matcher, Jeremy DB + learning engine)
          |
          +---> Phase 2 (parallel: Aaron portal scraping, Sapna scrapers+filter, Jeremy web app)
                  |
                  +---> Phase 3 (sequential merge: portal -> intel -> delivery)
                          |
                          +---> Phase 4 (polish + demo)
```

Critical path: 0.5 (mock data) to 0.7 (push) to A1.1-A1.2 (calculus) to A2.2 (adapter) to A2.7 (scraper) to I3.1-I3.10 (integration) to P4.6 (demo).

The BLOCKER is Phase 0.5 — mock data. Without it, nobody can test independently.

---

## 6. Integration Protocol (smooth team integration)

### Git Workflow
1. Jeremy scaffolds and pushes to `main` first (Phase 0)
2. Each person creates their feature branch from `main`: `aaron/portal`, `sapna/intel`, `jeremy/delivery`
3. Never push to `main` directly (except Jeremy's initial scaffold)
4. Each person owns their directory — no cross-directory edits without team agreement
5. Shared files (config.py, requirements.txt, data/ schemas) managed by Jeremy
6. Merge only at checkpoints (Phase 3)

### Communication Protocol
| Event | Action |
|-------|--------|
| Schema change | Message team + update data/mock/ files + update HANDOFF.md |
| Blocked on dependency | Use mock data, continue building |
| Module complete | Push to branch, notify team |
| Checkpoint reached | All pull from main, test together |
| Bug in someone else's module | File GitHub issue, do not fix their code |

### Integration Checklist (before each merge)
- [ ] All tests pass on your branch: `python -m pytest tests/ -v`
- [ ] Your output JSON matches the contract schema exactly
- [ ] No hardcoded secrets (credentials from .env only)
- [ ] Your __init__.py exports the clean API functions
- [ ] You have not edited files outside your owned directory
- [ ] Code reviewed by python-reviewer agent

### Anti-Integration-Failure Rules
1. Mock data files in `data/mock/` are the source of truth for schemas. If your module's output doesn't match the mock, fix YOUR module, not the mock.
2. Each __init__.py must export functions that take primitive args (dicts, strings, numbers) and return dicts matching contracts. No cross-package imports in __init__.py signatures.
3. The orchestrator imports from `portal`, `intelligence`, `delivery` packages. If those imports fail, the orchestrator falls back to mock data with a warning.
4. All modules must handle missing/empty data gracefully (return empty lists, not crash).

---

## 7. Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| KP portal 15-min lockout | High | High | Always logout in finally block. Add jitter between scrapes. Cache last scrape. |
| WebCMD CLI flag misuse (session/profile/browser run) | Medium | High | Corrections verified and documented in A2.3 NOTE. Smoke test early. |
| WebCMD not installed / wrong version | Medium | High | Phase 0.4 verifies with `webcmd doctor`. Node.js 20.6+ requirement. |
| Internshala Cloudflare block | Medium | Medium | curl_cffi with impersonate=chrome120. Fallback to GitHub internship repos. |
| NoBroker API is speculative | Medium | Medium | Smoke test early; fall back to mock housing data for the demo. |
| Schema drift between team members | High | High | Mock data is source of truth. Integration checklist enforces schema match. |
| Python 3.14 wheel gaps (curl_cffi/sklearn) | Medium | Medium | If pip install fails, fall back to a 3.12 venv. |
| Merge conflicts at Checkpoint 3 | High | Medium | Each person owns their dir. Only shared files (config.py, requirements.txt) may conflict. |
| Frontend eats hackathon time | Medium | Medium | Vanilla JS + static files, no build step. Layout polish deferred to Phase 4. |
| No sample LaTeX resume available | Medium | Low | Jeremy created data/sample_resume.tex in Phase 0.6. |

---

## 8. Session Log

| Date | Who | What was done | What was learned |
|------|-----|---------------|------------------|
| 2026-08-22 | Orchestrator | Analyzed codebase, installed skills, created HANDOFF.md, produced phased plan | Project is greenfield. WebCMD skills already available globally. Stale remote branches pruned. |
| 2026-08-22 | Jeremy | **Pivot to website delivery** — FastAPI + vanilla JS replaces Discord webhook/bot. Updated plan, .env.example, requirements.txt. Scaffolded project + mock data. | JSON contracts made the pivot cheap: Aaron/Sapna unchanged. WebCMD `session create`/`browser run` flags corrected. |

<!-- Append new session entries below this line -->