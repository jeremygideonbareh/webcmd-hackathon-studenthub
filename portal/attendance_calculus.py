"""
Attendance Calculus Engine for Atlas Portal Subsystem.

Given P (present), T (total), and threshold theta (default 85% / 0.85):

1. classes_can_skip = floor((P - theta*T) / theta)           if P/T >= theta, else 0
2. classes_must_attend = ceil((theta*T - P) / (1 - theta))   if P/T < theta, else 0
3. Risk Levels:
   - "SAFE"     if percentage >= 90.0%
   - "CAUTION"  if 85.0% <= percentage < 90.0%
   - "WARNING"  if 80.0% <= percentage < 85.0%
   - "DANGER"   if percentage < 80.0%
"""

import math
from datetime import datetime, timezone
from typing import Any, Dict, List, Union


def calculate_subject_risk(
    present: int,
    total: int,
    threshold: float = 0.85
) -> Dict[str, Any]:
    """
    Calculate attendance risk metrics and projection for a single subject.

    Args:
        present: Number of classes attended (P).
        total: Total number of classes held (T).
        threshold: Target minimum attendance ratio (e.g. 0.85 for 85%).

    Returns:
        Dictionary containing current percentage, can_skip, must_attend,
        risk_level, and human-readable projection message.
    """
    if total <= 0:
        return {
            "current_pct": 100.0,
            "classes_present": present,
            "classes_total": total,
            "classes_can_skip": 0,
            "classes_must_attend": 0,
            "risk_level": "SAFE",
            "projection": "No classes held yet. Attendance is currently at 100.0%."
        }

    present = max(0, min(present, total))
    pct = (present / total) * 100.0
    pct_rounded = round(pct, 2)
    threshold_pct = threshold * 100.0

    if pct >= threshold_pct:
        can_skip = math.floor((present - threshold * total) / threshold) if threshold > 0 else 0
        must_attend = 0
    else:
        can_skip = 0
        if threshold < 1.0:
            must_attend = math.ceil((threshold * total - present) / (1.0 - threshold))
        else:
            must_attend = 999

    if pct >= 90.0:
        risk_level = "SAFE"
    elif pct >= 85.0:
        risk_level = "CAUTION"
    elif pct >= 80.0:
        risk_level = "WARNING"
    else:
        risk_level = "DANGER"

    can_skip_clamped = max(0, int(can_skip))
    must_attend_clamped = max(0, int(must_attend))

    projection = _build_projection_message(
        risk_level=risk_level,
        pct=pct_rounded,
        can_skip=can_skip_clamped,
        must_attend=must_attend_clamped,
        threshold_pct=threshold_pct
    )

    return {
        "current_pct": pct_rounded,
        "classes_present": present,
        "classes_total": total,
        "classes_can_skip": can_skip_clamped,
        "classes_must_attend": must_attend_clamped,
        "risk_level": risk_level,
        "projection": projection
    }


def simulate_attendance(
    present: int,
    total: int,
    future_attend: int = 0,
    future_miss: int = 0,
    threshold: float = 0.85
) -> Dict[str, Any]:
    """Simulate projected attendance percentage after future attended & missed classes."""
    new_present = max(0, present + max(0, future_attend))
    new_total = max(1, total + max(0, future_attend) + max(0, future_miss))
    res = calculate_subject_risk(new_present, new_total, threshold=threshold)
    res["future_attend"] = future_attend
    res["future_miss"] = future_miss
    return res


def _build_projection_message(
    risk_level: str,
    pct: float,
    can_skip: int,
    must_attend: int,
    threshold_pct: float
) -> str:
    """Generate concise human-readable projection advice."""
    target = int(threshold_pct) if threshold_pct.is_integer() else threshold_pct
    if risk_level == "SAFE":
        if can_skip == 0:
            return f"You're at {pct}%. Solid standing, but maintain attendance to stay safely above {target}%."
        return f"You're at {pct}%. You can safely skip next {can_skip} class{'es' if can_skip != 1 else ''}."
    elif risk_level == "CAUTION":
        if can_skip == 0:
            return f"You're at {pct}%. Borderline safe ({target}% threshold). Avoid skipping upcoming classes."
        return f"You're at {pct}%. You can skip {can_skip} class{'es' if can_skip != 1 else ''} but proceed with caution."
    elif risk_level == "WARNING":
        return f"⚠️ Warning: You're at {pct}%. Must attend next {must_attend} consecutive class{'es' if must_attend != 1 else ''} to reach {target}%."
    else:
        return f"🚨 DANGER: Attendance is critically low at {pct}%. Must attend next {must_attend} consecutive class{'es' if must_attend != 1 else ''} immediately!"


def generate_risk_report(
    attendance_data: Dict[str, Any],
    threshold: float = 0.85
) -> Dict[str, Any]:
    """Generate risk_report.json schema compliant payload from attendance data."""
    subjects_input = attendance_data.get("subjects", [])
    evaluated_subjects = []

    for subj in subjects_input:
        present = subj.get("classes_present", 0)
        total = subj.get("classes_total", 0)
        metrics = calculate_subject_risk(present, total, threshold=threshold)

        evaluated_subjects.append({
            "code": subj.get("code", "UNKNOWN"),
            "name": subj.get("name", "Unknown Subject"),
            "current_pct": metrics["current_pct"],
            "classes_present": metrics["classes_present"],
            "classes_total": metrics["classes_total"],
            "classes_can_skip": metrics["classes_can_skip"],
            "classes_must_attend": metrics["classes_must_attend"],
            "projection": metrics["projection"],
            "risk_level": metrics["risk_level"]
        })

    evaluated_subjects.sort(key=lambda s: (s["current_pct"], -s["classes_must_attend"]))

    return {
        "generated_at": datetime.now(timezone.utc).astimezone().isoformat(),
        "threshold_pct": round(threshold * 100.0, 1),
        "student_id": attendance_data.get("student_id", "Unknown"),
        "student_name": attendance_data.get("student_name", "Unknown"),
        "semester": attendance_data.get("semester", "Current"),
        "subjects": evaluated_subjects
    }
