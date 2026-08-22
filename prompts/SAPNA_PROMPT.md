# 🧠 Sapna's Starting Prompt — Intelligence Architect

> Copy-paste everything below the line into your AI coding agent to get started.

---

## PROMPT START — COPY FROM HERE

I am Sapna, working on the **Atlas** hackathon project. My role is **Intelligence Architect**. I own the `intelligence/` directory in the repo at: https://github.com/sapnabalaji306-netizen/webcmd-hackathon-studenthub

I need you to help me build the **Intelligence Layer** — the brain of Atlas that parses resumes, scrapes job boards, matches internships to the student's profile using TF-IDF, and filters results based on GPA. Here's exactly what I need to build:

### My Responsibilities
1. **LaTeX Resume Parser** — Extract plain text from a .tex resume file using `pylatexenc` and regex for TF-IDF vectorization
2. **Job Board Scrapers** — Scrape internships from Internshala (using `curl_cffi` to bypass Cloudflare) and GitHub curated repos (SimplifyJobs)
3. **Housing Scraper** — Query NoBroker's internal REST API for rental listings (returns clean JSON, no HTML parsing needed)
4. **TF-IDF Matcher** — Compare resume text against job descriptions using scikit-learn's TfidfVectorizer with cosine similarity
5. **GPA-Gated Filter** — Dynamically adjust job recommendations based on student's GPA:
   - GPA >= 8.5: COMPETITIVE mode (include quant/trading/GPA-gated roles)
   - 8.0 <= GPA < 8.5: BALANCED mode (standard mix)
   - GPA < 8.0: PORTFOLIO mode (bias toward project-based/startup roles)

### Technical Details

**TF-IDF Optimization (IMPORTANT):**
- Use trigrams: `ngram_range=(1, 3)` to capture "machine learning", "REST API"
- Enable sublinear TF: `sublinear_tf=True` to prevent keyword-stuffed descriptions from dominating
- Preserve tech terms before tokenization: C++ → cpp_lang, C# → csharp_lang, Node.js → nodejs
- Custom stop words: strip recruitment jargon ("responsibilities", "requirements", "candidate")
- Final score formula: `(cosine_similarity * 0.6) + (skill_overlap * 0.3) + (preference_weight * 0.1)`

**Internshala Scraping:**
- Use `curl_cffi` with `impersonate="chrome120"` to bypass Cloudflare
- CSS selectors: `div.individual_internship`, `h3.job-internship-name`, `p.company-name`, `span.stipend`
- URL pattern: `https://internshala.com/internships/{category}-internship/page-{n}`

**NoBroker REST API (Housing):**
- Endpoint: `https://www.nobroker.in/api/v3/multi/property/filter/rent/filter`
- Returns clean JSON — no HTML parsing needed!
- Params: `searchParam`, `city`, `rent` range, `type` (BHK1,BHK2,ROOM), `furnishing`

**Resume Parsing:**
- Use `pylatexenc.latex2text.LatexNodes2Text` for full text extraction (for TF-IDF)
- Use regex fallback: `\section{SectionName}` pattern to extract structured sections
- Strip LaTeX commands: `\textbf{}`, `\textit{}`, `\href{}{}`

### Output Contracts (JSON schemas I must produce)

**resume_profile.json (internal):**
```json
{
  "name": "Rahul Kumar",
  "skills": ["Python", "MATLAB", "C", "TensorFlow", "React"],
  "education": "B.Tech Computer Science",
  "experience_summary": "Built ML pipeline...",
  "full_text": "(entire resume as plain text for TF-IDF)",
  "parsed_at": "2026-08-22T10:00:00+05:30"
}
```

**filtered_jobs.json (→ Jeremy's orchestrator):**
```json
{
  "generated_at": "2026-08-22T10:00:00+05:30",
  "student_gpa": 8.45,
  "gpa_mode": "competitive",
  "jobs": [
    {
      "id": "internshala_12345",
      "title": "Python Developer Intern",
      "company": "TechCorp",
      "match_score": 0.87,
      "match_reason": "Skills match: Python, REST APIs. GPA eligible.",
      "stipend": "₹15,000/month",
      "url": "https://internshala.com/internship/detail/12345",
      "category": "engineering"
    }
  ]
}
```

**housing_raw.json (→ Jeremy's orchestrator):**
```json
{
  "scraped_at": "2026-08-22T10:00:00+05:30",
  "source": "nobroker",
  "listings": [
    {
      "id": "nb_98765",
      "title": "2BHK near VIT Campus",
      "price": "₹12,000/month",
      "location": "Katpadi, Vellore",
      "url": "https://nobroker.in/property/98765",
      "bedrooms": 2,
      "furnished": "Semi-Furnished"
    }
  ]
}
```

### Input I Consume
- `data/gpa.json` from Aaron (or `data/mock/gpa.json` before integration)
- `preference_weights` dict from Jeremy's SQLite ledger (or empty dict `{}` before integration)
- A `.tex` resume file from `data/sample_resume.tex`

### File Structure I Own
```
intelligence/
├── __init__.py              # Clean API: get_matched_jobs(gpa, weights), get_housing()
├── resume_parser.py         # LaTeX → plain text + structured sections
├── job_scraper.py           # Internshala + GitHub repo scrapers
├── housing_scraper.py       # NoBroker REST API scraper
├── matcher.py               # TF-IDF + cosine similarity engine
└── gpa_filter.py            # GPA-gated filtering (competitive/balanced/portfolio)
```

### My Branch
I work on branch `sapna/intel`. I never push to `main` directly.

### Python Dependencies I Need
```
scikit-learn>=1.3.0
numpy>=1.24.0
pylatexenc>=2.10
TexSoup>=0.3.1
curl_cffi>=0.7.0
beautifulsoup4>=4.12.0
requests>=2.31.0
```

### My Timeline
- Hours 0-1: Set up branch, install deps, study sample .tex resume format
- Hours 1-2: Implement LaTeX resume parser with pylatexenc
- Hours 2-3: Build Internshala scraper with curl_cffi
- Hours 3-4: Implement TF-IDF matcher with trigrams, sublinear TF, tech-term preservation
- Hours 4-5: Implement GPA-gated filter logic
- Hours 5-6: Build NoBroker housing scraper (REST API), create clean `__init__.py` API
- Hours 6-7: Write unit tests for matcher, create mock outputs
- Hour 7: 🔗 MAJOR INTEGRATION with team

Please start by creating the file structure and implementing the TF-IDF matcher first (it's the core intelligence). Then the resume parser, then the scrapers.
