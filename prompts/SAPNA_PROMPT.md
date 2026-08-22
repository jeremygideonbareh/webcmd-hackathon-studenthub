# 🧠 Sapna's Master Task Plan & Starting Prompt — Intelligence Architect

> **Instructions for Sapna:** Copy and paste the prompt below into your AI coding agent (e.g. Gemini / Antigravity / Cursor). All functions and clean contract interfaces are already scaffolded and tested on `main`.

---

## PROMPT START — COPY FROM HERE

```markdown
Role: Intelligence Architect (Sapna)
Repository: https://github.com/jeremygideonbareh/webcmd-hackathon-studenthub
Branch to Work On: sapna/intel

Your goal is to build and expand the Intelligence Subsystem under `intelligence/` and `intel/`.

### 🎯 Your 4 Core Deliverables

1. **AI Resume & Skills Advisor Engine (`intelligence/advisor.py`)**:
   - Perform skill gap analysis across 4 major student streams:
     - **Engineering**: Check for Python, DSA, Git, Docker, REST APIs, SQL.
     - **Psychology**: Check for SPSS, Statistical Analysis, Qualtrics, R, Behavioral Assessment, Psychometrics.
     - **BBA**: Check for Excel Pivot Tables, Financial Modeling, Market Research, Brand Strategy, Sales Pitching, CRM.
     - **MBA**: Check for Corporate Strategy, Business Analytics, SQL, Tableau/PowerBI, DCF Valuation, Agile.
   - Output Dictionary:
     ```python
     {
         "stream": "Psychology",
         "readiness_score": 85,
         "matched_skills": ["SPSS", "Qualtrics"],
         "missing_critical_skills": ["R", "Psychometrics"],
         "recommended_projects": [
             {"title": "Empirical Behavioral Survey & Statistical Report", "description": "...", "skills_gained": ["SPSS", "ANOVA"]}
         ],
         "resume_bullet_suggestions": [
             "Conducted quantitative statistical analysis on sample of 500+ participants using SPSS ANOVA and regression models."
         ]
     }
     ```

2. **Scholarship Aggregator & Matcher (`intelligence/scholarships.py`)**:
   - Filter active scholarships from `data/mock/scholarships.json` by student CGPA and stream:
     ```python
     def get_scholarships(gpa: float = 8.0, stream: str = "Engineering") -> list[dict]:
     ```

3. **Student Deals & Perks Finder (`intelligence/discounts.py`)**:
   - Categorize student deals (Developer tools, Productivity, Research software, Finance, Subscriptions):
     ```python
     def get_discounts(category: str | None = None, stream: str | None = None) -> list[dict]:
     ```

4. **TF-IDF Resume & Job Matcher (`intel/parse_resume.py` & `intel/tfidf_matcher.py`)**:
   - Extract resume skills (LaTeX/PDF parser) and compute cosine similarity job match scores against scraped Internshala internship postings.

---

### 📦 Export Contract (`intelligence/__init__.py`)

Ensure your module cleanly exports these functions so Jeremy's FastAPI backend endpoints (`/api/advisor/analyze`, `/api/scholarships`, `/api/discounts`) can consume them without errors:

```python
from intelligence.advisor import analyze_resume_skills
from intelligence.scholarships import get_scholarships
from intelligence.discounts import get_discounts

__all__ = [
    "get_matched_jobs",
    "get_housing",
    "analyze_resume_skills",
    "get_scholarships",
    "get_discounts",
]
```

---

### 🧪 Verification Command

Run pytest to verify your code passes all unit tests:
```bash
python -m pytest tests/test_advisor.py tests/test_scholarships.py tests/test_discounts.py -v
```
```

---
