"""Atlas intelligence package — Sapna's domain. Resume parsing, scraping, matching."""
# intelligence/__init__.py
"""
Public interface for the Intelligence Subsystem.

Exposes a clean set of functions for Jeremy's FastAPI backend to consume
via /api/advisor/analyze, /api/scholarships, /api/discounts, and any
job/housing endpoints, without needing to know about the internal
module structure of intelligence/ or intel/.
"""

from intelligence.advisor import analyze_resume_skills
from intelligence.scholarships import get_scholarships
from intelligence.discounts import get_discounts
from intelligence.jobs import get_matched_jobs
from intelligence.housing import get_housing

__all__ = [
    "get_matched_jobs",
    "get_housing",
    "analyze_resume_skills",
    "get_scholarships",
    "get_discounts",
]