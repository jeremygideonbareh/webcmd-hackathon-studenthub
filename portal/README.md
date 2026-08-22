# 🔧 Portal Subsystem — Atlas

Owned by **Aaron** (Portal Engineer)  
Branch: `aaron/portal`

## Overview
The Portal subsystem automates data extraction from the university's Apache Struts Knowledge Pro (KP) portal using headless Chromium via WebCMD. It performs attendance risk calculus and extracts GPA signals to power downstream intelligence and delivery engines.

---

## Directory Structure
```
portal/
├── __init__.py                # Clean API: get_attendance(), get_risk_report(), get_gpa()
├── webcmd_adapter.py          # Subprocess wrapper for WebCMD CLI + caching & retries
├── attendance_extractor.py    # HTML parser handling Struts merged table cells
├── attendance_calculus.py     # Pure math engine for skip/attend formulas & risk tiers
├── gpa_extractor.py           # CGPA/SGPA parser & trend detection
├── run_portal.py              # CLI test runner
└── adapters/
    ├── kp_attendance_adapter.js  # WebCMD JS adapter for attendance extraction
    └── kp_gpa_adapter.js         # WebCMD JS adapter for GPA extraction
```

---

## Mathematical Formulas

Given present classes $P$, total classes $T$, and threshold $\theta$ (default $0.85$):

1. **Classes Allowed to Skip** ($\text{pct} \ge \theta \times 100$):
   $$\text{can\_skip} = \left\lfloor \frac{P - \theta \cdot T}{\theta} \right\rfloor$$

2. **Classes Required to Attend Consecutively** ($\text{pct} < \theta \times 100$):
   $$\text{must\_attend} = \left\lceil \frac{\theta \cdot T - P}{1 - \theta} \right\rceil$$

3. **Risk Bands**:
   - `SAFE`: $\ge 90.0\%$
   - `CAUTION`: $85.0\% \le \text{pct} < 90.0\%$
   - `WARNING`: $80.0\% \le \text{pct} < 85.0\%$
   - `DANGER`: $< 80.0\%$

---

## Shared Contracts Produced

- `data/attendance.json` → Consumed by Orchestrator (Jeremy)
- `data/risk_report.json` → Consumed by Orchestrator (Jeremy)
- `data/gpa.json` → Consumed by Intelligence Layer (Sapna) & Orchestrator (Jeremy)

---

## Quick Start & Verification

```bash
# Run unit tests
python -m unittest discover tests -v

# Run portal CLI with mock data
python portal/run_portal.py --mock

# Run live scrape (requires WebCMD and KP credentials)
python portal/run_portal.py --live
```
