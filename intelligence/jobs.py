# intelligence/jobs.py
"""
Thin wrapper connecting the intel/ TF-IDF matcher + Internshala scraper
to the intelligence package's public interface, so FastAPI endpoints
can call one clean function instead of reaching into intel/ directly.
"""

from typing import List, Dict, Any

from internshala_scraper import fetch_internships
from tfidf_matcher import match_resume_to_postings


def get_matched_jobs(
    resume_data: Dict[str, Any],
    category: str = "python-internship",
    top_n: int = 5,
) -> List[Dict[str, Any]]:
    """
    Fetch live internship postings and rank them against a parsed resume.

    Args:
        resume_data: dict with 'skills' and 'projects' lists, as produced
                     by intel/parse_resume.py
        category: Internshala category slug to search (e.g. "python-internship")
        top_n: how many top-ranked postings to return

    Returns:
        list of postings, each with an added 'match_score' field, sorted
        by relevance descending.
    """
    postings = fetch_internships(category=category)
    return match_resume_to_postings(resume_data, postings, top_n=top_n)


if __name__ == "__main__":
    import json

    sample_resume = {
        "skills": ["Python", "Qiskit", "Machine Learning"],
        "projects": ["Quantum Monte Carlo Option Pricing"],
    }
    results = get_matched_jobs(sample_resume, top_n=3)
    print(json.dumps(results, indent=2))