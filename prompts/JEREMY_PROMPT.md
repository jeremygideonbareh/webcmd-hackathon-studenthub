# 🎯 Jeremy's Starting Prompt — Integration Commander

> Copy-paste everything below the line into your AI coding agent to get started.

---

## PROMPT START — COPY FROM HERE

I am Jeremy, working on the **Atlas** hackathon project. My role is **Integration Commander**. I own the `delivery/` directory AND the root-level orchestrator in the repo at: https://github.com/jeremygideonbareh/webcmd-hackathon-studenthub

I am responsible for:
1. **Project scaffolding** — Setting up the entire project structure, config files, requirements.txt, .env.example, and mock data for the team
2. **Discord Webhook Sender** — Rich embedded messages with color-coded attendance alerts, job listings, and housing results
3. **Discord Bot** — Reaction listener using `on_raw_reaction_add` (NOT `on_reaction_add` — critical difference!)
4. **Self-Learning Engine** — Maps emoji reactions to preference weight updates stored in SQLite
5. **SQLite Database** — Tracks reactions, preference weights, and digest history
6. **Main Orchestrator** — The pipeline that ties Aaron's portal scraper + Sapna's intelligence layer + my Discord delivery together

### My Responsibilities in Detail

**1. Project Scaffolding (FIRST PRIORITY — Hour 0)**
I need to create:
- `requirements.txt` with all team dependencies
- `.env.example` with placeholder credentials
- `.gitignore` (Python standard + .env + data/*.json)
- `config.py` (loads .env + config.yaml)
- `config.yaml` (thresholds, URLs, scraper settings)
- `data/mock/` directory with mock JSON files matching ALL contracts so Aaron and Sapna can test independently

**2. Discord Webhook (Hours 2-3)**
- Use `?wait=true` query param to get message ID back (needed for reaction tracking)
- Handle `429` rate limits with `retry_after`
- Max 10 embeds per message
- Color-code by risk: SAFE=green(0x2ecc71), CAUTION=yellow(0xf39c12), WARNING=orange(0xe67e22), DANGER=red(0xe74c3c)

**3. Discord Bot (Hours 4-5)**
- MUST use `on_raw_reaction_add(payload)` — NOT `on_reaction_add(reaction, user)`
- `on_reaction_add` requires messages in bot cache — silently fails on uncached webhook messages!
- Auto-react to webhook messages with 👍👎⭐🚫 as feedback buttons
- Emoji mapping: 👍=boost 1.2x, 👎=suppress 0.8x, ⭐=favorite 1.5x, 🚫=block 0.3x

**4. Self-Learning Engine (Hours 5-6)**
- Weights clamped to [0.1, 3.0] to prevent runaway amplification
- On each pipeline run, load weights from SQLite → pass to Sapna's TF-IDF matcher
- Categories extracted from job metadata (skills, source, type)

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
# 5. Build digest payload
# 6. Send via Discord webhook → get message_id
# 7. Log digest to SQLite history
```

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
├── discord_webhook.py       # Rich embed sender with ?wait=true
├── discord_bot.py           # Reaction listener (on_raw_reaction_add)
├── learning_engine.py       # Emoji → weight update engine
└── database.py              # SQLite CRUD operations

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
discord-webhook>=1.3.0
discord.py>=2.3.0
python-dotenv>=1.0.0
pyyaml>=6.0
requests>=2.31.0
```

### My Branch
I work on branch `jeremy/delivery`. For scaffolding, I can push initial structure to `main`.

### My Timeline
- Hour 0: **SCAFFOLD EVERYTHING** — create project structure, config, requirements, .gitignore, .env.example
- Hour 0-1: Create ALL mock data files so Aaron and Sapna can test independently
- Hours 1-2: Set up SQLite schema, implement database.py
- Hours 2-3: Implement Discord webhook sender with rich embeds
- Hours 3-4: Implement orchestrator skeleton (works with mock data)
- Hours 4-5: Implement Discord bot with on_raw_reaction_add
- Hours 5-6: Implement self-learning engine, wire to SQLite
- Hours 6-7: Feed preference weights back into orchestrator pipeline
- Hour 7: 🔗 MAJOR INTEGRATION — replace mock data with real modules from Aaron and Sapna
- Hours 7-9: Wire real modules, implement GPA feedback loop, polish digest format
- Hours 9-10: Code freeze, demo prep

Please start by scaffolding the entire project structure with all mock data files. This is the MOST CRITICAL first step because Aaron and Sapna depend on having mock data to test against.
