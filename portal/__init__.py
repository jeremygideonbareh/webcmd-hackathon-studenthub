"""
Portal package — KP Knowledge Pro portal attendance & GPA extraction.
"""

from __future__ import annotations

import math
from typing import Dict, List, Any


def calculate_risk(present: int, total: int, threshold: float = 0.85) -> Dict[str, Any]:
    """Calculate attendance risk metrics for a single subject."""
    pct = round((present / total) * 100, 2) if total > 0 else 0.0

    if pct >= threshold * 100:
        can_skip = math.floor((present - threshold * total) / threshold)
        must_attend = 0
    else:
        can_skip = 0
        must_attend = math.ceil((threshold * total - present) / (1 - threshold))

    if pct >= 90:
        risk = "SAFE"
    elif pct >= 85:
        risk = "CAUTION"
    elif pct >= 80:
        risk = "WARNING"
    else:
        risk = "DANGER"

    return {
        "current_pct": pct,
        "classes_present": present,
        "classes_total": total,
        "classes_can_skip": max(0, can_skip),
        "classes_must_attend": max(0, must_attend),
        "risk_level": risk,
    }


def get_attendance() -> Dict[str, Any]:
    """Return latest portal attendance data."""
    return {
        "student_name": "Rahul Kumar",
        "student_id": "22BCE1234",
        "semester": "Fall 2026",
        "subjects": [
            {"code": "EEE1001", "name": "Basic Electrical Engineering", "classes_present": 42, "classes_total": 52},
            {"code": "CSE2001", "name": "Data Structures & Algorithms", "classes_present": 48, "classes_total": 50},
            {"code": "MAT2002", "name": "Discrete Mathematics", "classes_present": 35, "classes_total": 45},
            {"code": "PHY1001", "name": "Engineering Physics", "classes_present": 28, "classes_total": 40},
        ],
    }


def get_gpa() -> Dict[str, Any]:
    """Return latest portal GPA data."""
    return {
        "student_id": "22BCE1234",
        "current_cgpa": 8.45,
        "semester_gpa": 8.72,
        "gpa_trend": "stable",
    }