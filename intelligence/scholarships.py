# intelligence/scholarships.py
"""
Scholarship Aggregator & Matcher.

Filters a mock scholarship dataset by a student's CGPA and academic
stream, returning only the scholarships they're actually eligible for.
"""

import json
import os
from typing import List, Dict, Any

# Path to the mock data file, relative to this file's location so it
# works regardless of the current working directory the caller runs from.
_DATA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "mock", "scholarships.json",
)


def _load_scholarships() -> List[Dict[str, Any]]:
    """Load the mock scholarship dataset from disk."""
    with open(r"C:\Users\Sapna\hello\scholarships.json", "r", encoding="utf-8") as f:
        return json.load(f)

def get_scholarships(gpa: float = 8.0, stream: str = "Engineering") -> List[Dict[str, Any]]:
    """
    Return scholarships the student is eligible for, based on GPA and stream.

    Args:
        gpa: student's CGPA (e.g. 8.2)
        stream: one of "Engineering", "Psychology", "BBA", "MBA"

    Returns:
        list of scholarship dicts the student qualifies for, sorted by
        deadline (soonest first).
    """
    all_scholarships = _load_scholarships()

    eligible = [
        s for s in all_scholarships
        if gpa >= s.get("min_gpa", 0) and stream in s.get("streams", [])
    ]

    # Sort by deadline (soonest first) — deadlines are ISO date strings so
    # plain string sort works correctly here.
    eligible.sort(key=lambda s: s.get("deadline", "9999-12-31"))

    return eligible


if __name__ == "__main__":
    # Quick manual test
    results = get_scholarships(gpa=8.5, stream="Engineering")
    print(f"Found {len(results)} eligible scholarships:\n")
    for s in results:
        print(f"- {s['name']} ({s['amount']}) — deadline {s['deadline']}")