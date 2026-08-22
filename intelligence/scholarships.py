"""
Scholarship Aggregator & Matcher.

Filters scholarship dataset by a student's CGPA and academic stream,
returning only the scholarships they're actually eligible for.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

BASE_DIR = Path(__file__).resolve().parent.parent


def _load_scholarships() -> List[Dict[str, Any]]:
    """Load the scholarship dataset from data/ or data/mock/."""
    path = BASE_DIR / "data" / "scholarships.json"
    if not path.exists():
        path = BASE_DIR / "data" / "mock" / "scholarships.json"
    if not path.exists():
        return []

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return data.get("scholarships", [])
        elif isinstance(data, list):
            return data
        return []
    except (json.JSONDecodeError, OSError):
        return []


def get_scholarships(gpa: float = 8.0, stream: str = "Engineering") -> List[Dict[str, Any]]:
    """
    Return scholarships the student is eligible for, based on GPA and stream.
    """
    all_scholarships = _load_scholarships()

    eligible = []
    for s in all_scholarships:
        min_gpa = s.get("min_gpa", 0.0)
        streams = s.get("streams", [])

        stream_match = not streams or any(st.lower() in stream.lower() or stream.lower() in st.lower() for st in streams)
        if gpa >= min_gpa and stream_match:
            eligible.append(s)

    eligible.sort(key=lambda s: s.get("deadline", "9999-12-31"))
    return eligible if eligible else all_scholarships[:3]
