# 🔧 Aaron's Starting Prompt — Portal Engineer

> Copy-paste everything below the line into your AI coding agent to get started.

---

## PROMPT START — COPY FROM HERE

I am Aaron, working on the **Atlas** hackathon project. My role is **Portal Engineer**. I own the `portal/` directory in the repo at: https://github.com/jeremygideonbareh/webcmd-hackathon-studenthub

I need you to help me build the **KP Portal scraping engine** using **WebCMD** (`@agentrhq/webcmd`). Here's exactly what I need to build:

### My Responsibilities
1. **WebCMD Adapter** — A JavaScript adapter script that automates the Knowledge Pro (KP) student portal using headless Chromium
2. **Python Wrapper** — A Python class that calls the WebCMD adapter via subprocess and returns structured JSON
3. **Attendance Extractor** — Parse HTML tables from the KP portal to extract P (present) and T (total) values per subject
4. **Attendance Calculus Engine** — Calculate:
   - How many classes a student can skip while staying above 85% threshold: `can_skip = floor((P - θ*T) / θ)`
   - How many classes must be attended to reach 85%: `must_attend = ceil((θ*T - P) / (1 - θ))`
   - Risk levels: SAFE (>90%), CAUTION (85-90%), WARNING (80-85%), DANGER (<80%)
5. **GPA Extractor** — Extract CGPA and SGPA from the grades page

### Technical Details

**KP Portal Architecture:**
- Platform: Apache Struts (Java) at `kp.christuniversity.in/KnowledgePro`
- Login: POST to `StudentLogin.do?method=loginStudent` with `userName` + `password`
- Session: Java `JSESSIONID` cookie
- Attendance page: `StudentLogin.do?method=initStudentWiseAttendanceSummary`
- ⚠️ CRITICAL: 15-minute account lockout if you don't logout properly! Always call `StudentLogin.do?method=logout` in a finally block.
- Data is in legacy HTML `<table>` elements with merged cells

**WebCMD Setup:**
```bash
npm install -g @agentrhq/webcmd
webcmd doctor
webcmd session create --profile kp_student -f json
```

**WebCMD Adapter Pattern:**
```bash
# Run adapter and get JSON output:
webcmd --profile kp_student browser run --file portal/adapters/kp_attendance_adapter.js -f json
```

### Output Contracts (JSON schemas I must produce)

**attendance.json:**
```json
{
  "student_name": "Rahul Kumar",
  "student_id": "22BCE1234",
  "semester": "Fall 2026",
  "scraped_at": "2026-08-22T10:00:00+05:30",
  "subjects": [
    {
      "code": "EEE1001",
      "name": "Basic Electrical Engineering",
      "classes_present": 42,
      "classes_total": 52,
      "attendance_pct": 80.77,
      "status": "WARNING"
    }
  ]
}
```

**risk_report.json:**
```json
{
  "generated_at": "2026-08-22T10:00:00+05:30",
  "threshold_pct": 85.0,
  "subjects": [
    {
      "code": "EEE1001",
      "name": "Basic Electrical Engineering",
      "current_pct": 80.77,
      "classes_present": 42,
      "classes_total": 52,
      "classes_can_skip": 0,
      "classes_must_attend": 3,
      "projection": "Must attend next 3 consecutive classes to reach 85%",
      "risk_level": "HIGH"
    }
  ]
}
```

**gpa.json:**
```json
{
  "student_id": "22BCE1234",
  "current_cgpa": 8.45,
  "semester_gpa": 8.72,
  "scraped_at": "2026-08-22T10:00:00+05:30",
  "gpa_trend": "stable"
}
```

### File Structure I Own
```
portal/
├── __init__.py              # Clean API: get_attendance(), get_gpa()
├── webcmd_adapter.py        # Python wrapper around WebCMD CLI
├── adapters/
│   ├── kp_attendance_adapter.js  # WebCMD JS adapter for attendance
│   └── kp_gpa_adapter.js        # WebCMD JS adapter for GPA
├── attendance_extractor.py  # HTML table parser
├── attendance_calculus.py   # Floor/ceiling math engine
└── gpa_extractor.py         # CGPA/SGPA extraction
```

### My Branch
I work on branch `aaron/portal`. I never push to `main` directly.

### Edge Cases I Must Handle
- 15-minute lockout: Always logout in `finally` blocks
- JSESSIONID expiry: Detect redirect to login page, re-authenticate
- CAPTCHA on rapid logins: Add 5-15 min random jitter between scrapes
- Legacy HTML tables: Handle `colspan`/`rowspan` merged cells
- Portal maintenance: Cache last successful scrape, serve with staleness warning

### My Timeline
- Hours 0-1: Install WebCMD, test browser launch, study KP login form
- Hours 1-3: Implement WebCMD login flow, navigate to attendance page, extract P & T
- Hours 3-4: Implement attendance calculus, GPA extraction
- Hours 4-5: Handle edge cases, error handling, retry logic
- Hours 5-6: Create clean `__init__.py` API, write unit tests
- Hour 7: 🔗 MAJOR INTEGRATION with team

Please start by creating the file structure and implementing the attendance calculus engine first (it's pure Python math, no external dependencies, easy to test). Then move to the WebCMD adapter.
