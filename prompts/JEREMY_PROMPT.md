# 🎯 Jeremy's Starting Prompt — Integration Commander

> Copy-paste everything below the line into your AI coding agent to get started.

---

## PROMPT START — COPY FROM HERE

I am Jeremy, working on the **Atlas** hackathon project. My role is **Integration Commander**. I own the `web/` directory, the `delivery/` directory, AND the root-level orchestrator in the repo at: https://github.com/jeremygideonbareh/webcmd-hackathon-studenthub

> **PIVOT (2026-08-22):** Delivery is now a **FastAPI web dashboard**, NOT Discord. The Discord webhook/bot are cancelled (see HANDOFF.md).

I am responsible for:
1. **Project scaffolding** — Setting up the entire project structure, config files, requirements.txt, .env.example, and mock data for the team
2. **FastAPI Web Dashboard** — `web/app.py`: GET `/` (dashboard), GET `/api/digest` (reads `data/*.json`), POST `/api/feedback` (reaction buttons → learning engine)
3. **Dashboard UI** — `web/static/`: single-page attendance risk cards (color-coded), job cards with 👍👎⭐🚫 buttons, housing listings
4. **Self-Learning Engine** — Maps feedback reactions to preference weight updates stored in SQLite
5. **SQLite Database** — Tracks reactions, preference weights, and digest history
6. **Main Orchestrator** — The pipeline that ties Aaron's portal scraper + Sapna's intelligence layer + my web delivery together

### My Responsibilities in Detail

**1. Project Scaffolding (FIRST PRIORITY — Hour 0)**
I need to create:
- `requirements.txt` with all team dependencies
- `.env.example` with placeholder credentials
- `.gitignore` (Python standard + .env + data/*.json)
- `config.py` (loads .env + config.yaml)
- `config.yaml` (thresholds, URLs, scraper settings)
- `data/mock/` directory with mock JSON files matching ALL contracts so Aaron and Sapna can test independently

**2. Web Dashboard (Hours 2-4)**
- `web/app.py` — FastAPI app, serves `web/static/`, exposes `/api/digest` and `/api/feedback`
- `/api/digest` reads `data/attendance.json`, `data/risk_report.json`, `data/gpa.json`, `data/filtered_jobs.json`, `data/housing_raw.json` fresh on each call (graceful empty-data fallback)
- `/api/feedback` accepts `{item_type, item_id, reaction}` and calls `learning_engine.process_reaction()`
- Color-code by risk: SAFE=green(#2ecc71), CAUTION=yellow(#f39c12), WARNING=orange(#e67e22), DANGER=red(#e74c3c)

**3. Dashboard UI (web/static/)**
- Vanilla JS + CSS, no build step
- Sections: attendance risk cards, matched jobs (with reaction buttons), housing listings
- Reaction buttons POST to `/api/feedback`, show a subtle "learned ✓" state

**4. Self-Learning Engine (Hours 5-6)**
- Weights clamped to [0.1, 3.0] to prevent runaway amplification
- On each pipeline run, load weights from SQLite → pass to Sapna's TF-IDF matcher
- Categories extracted from job metadata (skills, source, type)
- Reaction mapping: 👍=boost 1.2x, 👎=suppress 0.8x, ⭐=favorite 1.5x, 🚫=block 0.3x

**5. SQLite Schema:**
```sql
CREATE TABLE reactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id TEXT NOT NULL,
    item_type TEXT NOT NULL,
    item_id TEXT NOT NULL,
    reaction TEXT NOT NULL,
    reacted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE preference_weights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL UNIQUE,
    weight REAL DEFAULT 1.0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE digest_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    digest_type TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**6. Orchestrator Pipeline (Hours 3-4, refined at Hour 7)**
```python
# The orchestrator flow:
# 1. Load config
# 2. Call Aaron's portal scraper → attendance.json, risk_report.json, gpa.json
# 3. Load preference weights from SQLite
# 4. Call Sapna's intelligence → filtered_jobs.json, housing_raw.json
# 5. Write digest data to data/*.json (dashboard reads it live)
# 6. (Optional) notify_discord.py if DISCORD_WEBHOOK_URL set
```
CLI modes: `python orchestrator.py --mock` (default, uses data/mock/), `--live` (real modules), `--live-demo` (real + demo flags).

### Input Contracts I Consume
- `data/attendance.json` from Aaron
- `data/risk_report.json` from Aaron  
- `data/gpa.json` from Aaron
- `data/filtered_jobs.json` from Sapna
- `data/housing_raw.json` from Sapna

### The GPA → InternRadar Feedback Loop (Hour 7-8)
I implement the critical logic: if GPA drops between scrapes, I pass the new GPA mode (competitive/balanced/portfolio) to Sapna's filter, which automatically adjusts job recommendations.

### File Structure I Own
```
delivery/
├── __init__.py
├── learning_engine.py       # Reaction → weight update engine
├── database.py              # SQLite CRUD operations
└── notify_discord.py        # OPTIONAL webhook bonus (DISCORD_WEBHOOK_URL)

web/
├── app.py                   # FastAPI dashboard
└── static/
    ├── index.html           # Dashboard page
    ├── app.js               # fetch digest + POST feedback
    └── style.css            # Risk color coding

# Root level (also mine):
orchestrator.py              # Main pipeline
config.py                    # Config loader
config.yaml                  # Settings
requirements.txt             # All dependencies
.env.example                 # Credential template
.gitignore                   # Standard Python gitignore
```

### Python Dependencies I Need
```
fastapi>=0.110.0
uvicorn>=0.29.0
python-dotenv>=1.0.0
pyyaml>=6.0
requests>=2.31.0
```

### My Branch
I work on branch `jeremy/delivery`. For scaffolding, I can push initial structure to `main`.

### My Timeline
- Hour 0: **SCAFFOLD EVERYTHING** — create project structure, config, requirements, .gitignore, .env.example
- Hour 0-1: Create ALL mock data files so Aaron and Sapna can test independently
- Hours 1-2: Set up SQLite schema, implement database.py + learning_engine.py
- Hours 2-4: Implement FastAPI dashboard (web/app.py + static UI + /api/feedback)
- Hours 3-4: Implement orchestrator skeleton (works with mock data)
- Hour 4: 🔗 **Checkpoint 2** — orchestrator --mock → dashboard shows digest live
- Hours 4-6: Wire learning engine to SQLite + /api/feedback buttons
- Hour 7: 🔗 MAJOR INTEGRATION — replace mock data with real modules from Aaron and Sapna
- Hours 7-9: Wire real modules, implement GPA feedback loop, polish dashboard
- Hours 9-10: Code freeze, demo prep

Please start by scaffolding the entire project structure with all mock data files. This is the MOST CRITICAL first step because Aaron and Sapna depend on having mock data to test against.