"""
Intelligence package — unifying resume parsing, TF-IDF matching,
job scrapers (Internshala), and housing scrapers (NoBroker).
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to sys.path so intel/ modules can be imported smoothly
ROOT = Path(__file__).resolve().parent.parent
INTEL_DIR = ROOT / "intel"
if str(INTEL_DIR) not in sys.path:
    sys.path.insert(0, str(INTEL_DIR))

try:
    from tfidf_matcher import match_resume_to_postings
    from internshala_scraper import fetch_internships
    from nobroker_housing_mock import fetch_listings as fetch_housing_mock
except ImportError as e:
    print(f"[intelligence] Warning: could not import intel modules ({e})")
    match_resume_to_postings = None
    fetch_internships = None
    fetch_housing_mock = None


def get_matched_jobs(resume_data: dict | None = None, category: str = "python-internship", top_n: int = 5) -> dict:
    """Fetch live Internshala postings and score them against the parsed resume profile."""
    if not fetch_internships or not match_resume_to_postings:
        return {"jobs": []}

    default_resume = {
        "skills": ["Python", "Machine Learning", "C++", "FastAPI", "React", "REST APIs"],
        "projects": ["Atlas StudentHub", "AI Search Engine", "Distributed Pipeline"],
    }
    profile = resume_data or default_resume

    try:
        raw_postings = fetch_internships(category=category)
        if not raw_postings:
            return {"jobs": []}

        matched = match_resume_to_postings(profile, raw_postings, top_n=top_n)

        formatted_jobs = []
        for i, m in enumerate(matched):
            formatted_jobs.append({
                "id": m.get("link") or f"job_{i}",
                "title": m.get("title", "Software Developer Intern"),
                "company": m.get("company", "Tech Enterprise"),
                "match_score": m.get("match_score", 0.85),
                "match_reason": f"Top resume match based on skills: {', '.join(m.get('skills', ['Python']))}",
                "stipend": m.get("stipend", "Competitive"),
                "url": m.get("link", "https://internshala.com"),
                "category": category,
            })
        return {"jobs": formatted_jobs}
    except Exception as err:
        print(f"[intelligence] Error matching jobs: {err}")
        return {"jobs": []}


def get_housing(locality: str = "Koramangala", city: str = "Bangalore", budget_max: int = 25000) -> dict:
    """Fetch housing listings near campus."""
    if not fetch_housing_mock:
        return {"listings": []}

    try:
        listings = fetch_housing_mock(locality=locality, city=city, budget_max=budget_max)
        formatted = []
        for i, h in enumerate(listings):
            formatted.append({
                "id": h.get("link") or f"housing_{i}",
                "title": h.get("title", "Apartment near campus"),
                "price": f"₹{h.get('price', '15,000')}/month" if isinstance(h.get("price"), (int, float)) else str(h.get("price", "₹15,000/month")),
                "location": f"{locality}, {city}",
                "url": h.get("link", "https://www.nobroker.in"),
                "bedrooms": h.get("bhk", 2),
                "furnished": "Semi-Furnished",
            })
        return {"listings": formatted}
    except Exception as err:
        print(f"[intelligence] Error fetching housing: {err}")
        return {"listings": []}