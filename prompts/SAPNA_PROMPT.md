# 🧠 Sapna's Starting Prompt — Intelligence Architect (Expanded Scope)

> Copy-paste everything below the line into your AI coding agent to get started.

---

## PROMPT START — COPY FROM HERE

I am Sapna, working on the **Atlas** hackathon project. My role is **Intelligence Architect**. I own the `intelligence/` directory in the repo at: https://github.com/jeremygideonbareh/webcmd-hackathon-studenthub

I am responsible for building the **Intelligence Layer** of Atlas, including:
1. **Stream-Tailored AI Resume & Skills Advisor (`intelligence/advisor.py`)**:
   - Stream benchmarks for **Engineering**, **Psychology**, **BBA**, and **MBA**.
   - Calculates Readiness Score (0-100%), missing critical skills, recommended portfolio projects, and resume bullet suggestions.
2. **Scholarship Aggregator & Matcher (`intelligence/scholarships.py`)**:
   - Filter scholarships by student GPA eligibility and academic stream.
3. **Student Discounts Catalog (`intelligence/discounts.py`)**:
   - Categorize student deals (Developer tools, Research software, Business courses, Hardware, Subscriptions).
4. **LaTeX Resume Parser & TF-IDF Matcher (`intel/parse_resume.py`, `intel/tfidf_matcher.py`)**:
   - Extract resume skills and compute cosine similarity job match scores.

### My Functions to Export (`intelligence/__init__.py`)

```python
def analyze_resume_skills(user_skills: list[str], stream: str = "Engineering") -> dict:
    ...

def get_scholarships(gpa: float = 8.0, stream: str = "Engineering") -> list[dict]:
    ...

def get_discounts(category: str | None = None, stream: str | None = None) -> list[dict]:
    ...

def get_matched_jobs(resume_data: dict | None = None, category: str = "python-internship", top_n: int = 5) -> dict:
    ...

def get_housing(locality: str = "Koramangala", city: str = "Bangalore", budget_max: int = 25000) -> dict:
    ...
```

### JSON Contracts I Read/Write

`data/mock/scholarships.json`:
```json
{
  "scholarships": [
    {
      "id": "sch_01",
      "title": "National Engineering Excellence Grant 2026",
      "provider": "Ministry of Education",
      "amount": "₹1,00,000 / year",
      "min_gpa": 8.0,
      "streams": ["Engineering", "Data Science"],
      "deadline": "2026-10-15",
      "description": "Merit-based aid for high-performing engineering students.",
      "url": "https://scholarships.gov.in"
    }
  ]
}
```

`data/mock/discounts.json`:
```json
{
  "discounts": [
    {
      "id": "disc_01",
      "title": "GitHub Student Developer Pack",
      "provider": "GitHub",
      "category": "Developer Tools",
      "discount": "100% FREE",
      "description": "Copilot, JetBrains, Canva Pro, DigitalOcean credits.",
      "streams": ["Engineering", "BBA", "MBA"],
      "code": "STUDENT-EDU-VERIFY",
      "url": "https://education.github.com/pack"
    }
  ]
}
```

### My Branch
I work on branch `sapna/intel`. I export clean Python dicts matching these contracts so Jeremy's API endpoints (`/api/advisor/analyze`, `/api/scholarships`, `/api/discounts`) consume them cleanly without merge conflicts.
