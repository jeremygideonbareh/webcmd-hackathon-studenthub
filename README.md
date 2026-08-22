# 🗺️ Atlas — StudentHub Hackathon Project

> **One platform that scrapes your college portal, calculates your attendance risk, finds you internships you're actually qualified for, and learns from your feedback — all delivered on a live web dashboard.**

---

## 🏗️ Architecture

Atlas has three main subsystems built by three team members working in parallel:

| Team Member | Role | Subsystem | Branch |
|------------|------|-----------|--------|
| **Aaron** | Portal Engineer | WebCMD + KP portal scraping + attendance calculus | `aaron/portal` |
| **Sapna** | Intelligence Architect | Resume parser + job/housing scrapers + TF-IDF matcher | `sapna/intel` |
| **Jeremy** | Integration Commander | Web dashboard (FastAPI) + self-learning engine + orchestrator | `jeremy/delivery` |

---

## 🚀 Quick Start

```bash
# 1. Clone & install
git clone https://github.com/jeremygideonbareh/webcmd-hackathon-studenthub.git
cd webcmd-hackathon-studenthub
pip install -r requirements.txt

# 2. Install WebCMD (requires Node.js 20.6+)
npm install -g @agentrhq/webcmd
webcmd doctor

# 3. Set up environment
cp .env.example .env
# Edit .env with your credentials

# 4. Run the full pipeline
python orchestrator.py --mock

# 5. Start the dashboard
uvicorn web.app:app --reload
# → open http://127.0.0.1:8000
```

---

## 📁 Project Structure

```
atlas/
├── IMPLEMENTATION_PLAN.md          # Full hackathon plan with team assignments
├── requirements.txt
├── .env.example
├── config.py / config.yaml
├── orchestrator.py                 # Main pipeline (Jeremy)
├── portal/                         # Aaron's domain
│   ├── webcmd_adapter.py
│   ├── kp_scraper.py
│   ├── attendance_calculus.py
│   └── gpa_extractor.py
├── intelligence/                   # Sapna's domain
│   ├── resume_parser.py
│   ├── job_scraper.py
│   ├── housing_scraper.py
│   ├── matcher.py
│   └── gpa_filter.py
├── delivery/                       # Jeremy's domain
│   ├── learning_engine.py
│   ├── database.py
│   └── notify_discord.py           # OPTIONAL webhook bonus
├── web/                            # Jeremy's domain — web delivery
│   ├── app.py                      # FastAPI dashboard
│   └── static/                     # index.html, app.js, style.css
├── data/mock/                      # Shared mock data for independent testing
└── prompts/                        # AI agent starting prompts per team member
    ├── AARON_PROMPT.md
    ├── SAPNA_PROMPT.md
    └── JEREMY_PROMPT.md
```

---

## 🤖 Getting Started with Your AI Agent

Each team member has a personalized starting prompt in `prompts/`. Copy-paste your prompt into your AI coding agent (Claude, Cursor, Gemini, etc.) to get started immediately.

| Who | Prompt File | What it builds |
|-----|-----------|---------------|
| **Aaron** | [`prompts/AARON_PROMPT.md`](prompts/AARON_PROMPT.md) | WebCMD adapter + KP portal scraper + attendance math |
| **Sapna** | [`prompts/SAPNA_PROMPT.md`](prompts/SAPNA_PROMPT.md) | Resume parser + Internshala scraper + TF-IDF matcher + housing scraper |
| **Jeremy** | [`prompts/JEREMY_PROMPT.md`](prompts/JEREMY_PROMPT.md) | FastAPI dashboard + reaction buttons + self-learning engine + orchestrator |

---

## 📋 Integration Checkpoints

| Hour | Checkpoint | What happens |
|------|-----------|-------------|
| 1 | 🔗 Checkpoint 1 | Everyone pulls from main, verify project structure |
| 4 | 🔗 Checkpoint 2 | Jeremy tests orchestrator with mock data |
| 7 | 🔗 Checkpoint 3 | **MAJOR**: All three merge to main, test full pipeline |
| 9 | 🔗 Checkpoint 4 | Full end-to-end with real data |

---

## 📊 Key Data Contracts

All modules communicate via JSON files in `data/`. See [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md) for full schemas.

| Contract | From → To | Description |
|----------|-----------|------------|
| `attendance.json` | Aaron → Jeremy | Attendance P, T values per subject |
| `risk_report.json` | Aaron → Jeremy | Classes to skip/attend, risk levels |
| `gpa.json` | Aaron → Sapna & Jeremy | CGPA, SGPA, trend |
| `filtered_jobs.json` | Sapna → Jeremy | Matched & GPA-filtered internships |
| `housing_raw.json` | Sapna → Jeremy | NoBroker rental listings |

---

## 🧠 The Self-Learning Loop

Click reaction buttons on job cards in the dashboard. Atlas learns your preferences:
- 👍 = Boost similar results (1.2x)
- 👎 = Suppress similar results (0.8x)
- ⭐ = Favorite (1.5x boost)
- 🚫 = Never show again (0.3x)

---

## 📜 License

MIT — Built for the WebCMD Hackathon 2026
