"""
GPA Extractor for Knowledge Pro (KP) Portal.

Extracts CGPA, SGPA, and semester grades from KP portal markup or API payloads.
Tracks historical GPA trends (improving, stable, declining) to provide signals
for downstream modules (like Sapna's GPA-Gated Job Matcher).
"""

import json
import os
import re
from datetime import datetime, timezone
from typing import Any, Dict, Optional

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False


def parse_gpa_html(
    html_content: str,
    student_id: Optional[str] = None,
    previous_gpa_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Parse KP portal grades HTML page into gpa.json schema dictionary.

    Args:
        html_content: Raw HTML text of the StudentWiseMarksSummary/Grades page.
        student_id: Student identifier if known.
        previous_gpa_path: Path to cached gpa.json to calculate trend.

    Returns:
        Structured gpa.json contract dictionary.
    """
    cgpa = 0.0
    sgpa = 0.0

    if HAS_BS4:
        soup = BeautifulSoup(html_content, "html.parser")
        cgpa = _extract_numeric_val_soup(soup, [r"CGPA", r"Cumulative\s*Grade\s*Point", r"Cumulative\s*GPA"])
        sgpa = _extract_numeric_val_soup(soup, [r"SGPA", r"Semester\s*Grade\s*Point", r"Semester\s*GPA", r"Current\s*GPA"])

    # Fallback to regex over full text if DOM search yielded 0
    if cgpa == 0.0:
        cgpa_match = re.search(r"CGPA\s*[:=\-]?\s*([0-9]+\.[0-9]+)", html_content, re.IGNORECASE)
        if not cgpa_match:
            cgpa_match = re.search(r"Cumulative\s*Grade\s*Point\s*Average\s*[:=\-]?\s*([0-9]+\.[0-9]+)", html_content, re.IGNORECASE)
        if not cgpa_match:
            # Match table cell pattern: <td>...CGPA...</td><td>8.45</td>
            cgpa_match = re.search(r"(?:CGPA|Cumulative\s*Grade\s*Point\s*Average[^<]*?)[^0-9<]*?</td>\s*<td[^>]*?>\s*([0-9]+\.[0-9]+)", html_content, re.IGNORECASE)
        if cgpa_match:
            cgpa = float(cgpa_match.group(1))

    if sgpa == 0.0:
        sgpa_match = re.search(r"SGPA\s*[:=\-]?\s*([0-9]+\.[0-9]+)", html_content, re.IGNORECASE)
        if not sgpa_match:
            sgpa_match = re.search(r"Semester\s*Grade\s*Point\s*Average\s*[:=\-]?\s*([0-9]+\.[0-9]+)", html_content, re.IGNORECASE)
        if not sgpa_match:
            sgpa_match = re.search(r"(?:SGPA|Semester\s*Grade\s*Point\s*Average[^<]*?)[^0-9<]*?</td>\s*<td[^>]*?>\s*([0-9]+\.[0-9]+)", html_content, re.IGNORECASE)
        if sgpa_match:
            sgpa = float(sgpa_match.group(1))

    # Detect trend based on previous scrape
    trend = compute_gpa_trend(cgpa, previous_gpa_path)

    return {
        "student_id": student_id or "Unknown",
        "current_cgpa": round(cgpa, 2),
        "semester_gpa": round(sgpa if sgpa > 0 else cgpa, 2),
        "scraped_at": datetime.now(timezone.utc).astimezone().isoformat(),
        "gpa_trend": trend
    }


def compute_gpa_trend(current_cgpa: float, previous_gpa_path: Optional[str] = None) -> str:
    """
    Compute whether GPA is improving, stable, or declining relative to previous cache.

    Args:
        current_cgpa: Current scraped CGPA
        previous_gpa_path: Filepath to previous gpa.json record

    Returns:
        'improving', 'stable', or 'declining'
    """
    if not previous_gpa_path or not os.path.exists(previous_gpa_path):
        return "stable"

    try:
        with open(previous_gpa_path, "r", encoding="utf-8") as f:
            prev_data = json.load(f)
            prev_cgpa = float(prev_data.get("current_cgpa", current_cgpa))
            diff = current_cgpa - prev_cgpa
            if diff > 0.05:
                return "improving"
            elif diff < -0.05:
                return "declining"
            else:
                return "stable"
    except Exception:
        return "stable"


def _extract_numeric_val_soup(soup: Any, regex_patterns: list) -> float:
    """Find float value near targeted label tags using BeautifulSoup."""
    for pattern in regex_patterns:
        elem = soup.find(string=re.compile(pattern, re.I))
        if elem:
            parent = elem.parent
            if parent:
                text = parent.get_text()
                val_match = re.search(r"([0-9]+\.[0-9]+)", text)
                if val_match:
                    try:
                        return float(val_match.group(1))
                    except ValueError:
                        pass
                
                next_sibling = parent.find_next_sibling(["td", "th", "span", "div"])
                if next_sibling:
                    val_match = re.search(r"([0-9]+\.[0-9]+)", next_sibling.get_text())
                    if val_match:
                        try:
                            return float(val_match.group(1))
                        except ValueError:
                            pass
    return 0.0
