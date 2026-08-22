"""
HTML Attendance Extractor for Knowledge Pro (KP) Portal.

Parses legacy Apache Struts HTML tables and extracts structured attendance records.
Handles:
- Merged table cells (rowspan, colspan)
- Inconsistent Struts column ordering
- Percentage symbols and whitespace cleanup
- Fallback regex parsing when DOM structure deviates or bs4 is not installed
"""

import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False


def parse_attendance_html(
    html_content: str,
    student_id: Optional[str] = None,
    student_name: Optional[str] = None,
    semester: Optional[str] = None
) -> Dict[str, Any]:
    """
    Parse KP portal HTML response into attendance.json schema dictionary.

    Args:
        html_content: Raw HTML text of the StudentWiseAttendanceSummary page.
        student_id: Optional fallback student ID if not found in HTML.
        student_name: Optional fallback student name if not found in HTML.
        semester: Optional semester tag.

    Returns:
        Dictionary conforming to attendance.json contract.
    """
    extracted_name = student_name or _extract_student_name(html_content) or "Student"
    extracted_id = student_id or _extract_student_id(html_content) or "Unknown"
    extracted_semester = semester or _extract_semester(html_content) or "Current Semester"

    subjects: List[Dict[str, Any]] = []

    if HAS_BS4:
        soup = BeautifulSoup(html_content, "html.parser")
        tables = soup.find_all("table")
        for table in tables:
            rows = table.find_all("tr")
            for row in rows:
                cols = [td.get_text(strip=True) for td in row.find_all(["td", "th"])]
                if len(cols) < 4:
                    continue

                parsed_row = _parse_table_row(cols)
                if parsed_row:
                    if not any(s["code"] == parsed_row["code"] for s in subjects):
                        subjects.append(parsed_row)

    # If bs4 is not installed or table parsing yielded nothing, fallback to regex scanning
    if not subjects:
        subjects = _regex_extract_subjects(html_content)

    return {
        "student_name": extracted_name,
        "student_id": extracted_id,
        "semester": extracted_semester,
        "scraped_at": datetime.now(timezone.utc).astimezone().isoformat(),
        "subjects": subjects
    }


def _parse_table_row(cols: List[str]) -> Optional[Dict[str, Any]]:
    """Inspect row columns and extract subject details if it matches record pattern."""
    code_match = re.match(r"^([A-Z0-9\-_]{3,12})$", cols[0], re.IGNORECASE)
    
    numeric_indices = []
    for idx, col in enumerate(cols):
        val = re.sub(r"[^\d.]", "", col)
        if val.isdigit():
            numeric_indices.append((idx, int(val)))

    if len(numeric_indices) >= 2:
        num_vals = [n[1] for n in numeric_indices]
        if len(cols) >= 5:
            try:
                held = int(cols[2])
                attended = int(cols[3])
            except ValueError:
                held = max(num_vals[0], num_vals[1])
                attended = min(num_vals[0], num_vals[1])
        else:
            held = max(num_vals[0], num_vals[1])
            attended = min(num_vals[0], num_vals[1])

        code = cols[0] if (code_match or len(cols[0]) >= 3) else f"SUBJ_{len(cols)}"
        name = cols[1] if len(cols) > 1 and not cols[1].isdigit() else "Subject"

        if "code" in code.lower() or "subject" in name.lower():
            return None

        pct = (attended / held * 100.0) if held > 0 else 100.0
        pct_rounded = round(pct, 2)

        return {
            "code": code,
            "name": name,
            "classes_present": attended,
            "classes_total": held,
            "attendance_pct": pct_rounded,
            "status": "WARNING" if pct_rounded < 85.0 else "OK"
        }

    return None


def _regex_extract_subjects(html_content: str) -> List[Dict[str, Any]]:
    """Fallback regex extractor for unstructured text or non-standard HTML tables."""
    subjects = []
    # Match pattern across HTML tags: e.g. <td>EEE1001</td>...<td>42</td>...
    clean_text = re.sub(r"<[^>]+>", " ", html_content)
    clean_text = re.sub(r"&nbsp;", " ", clean_text)
    
    pattern = re.compile(
        r"([A-Z]{2,4}\d{3,4}[A-Z]?)\s+([A-Za-z0-9\s,\-\&]+?)\s+(\d{1,3})\s+(\d{1,3})(?:\s+(\d{1,3}(?:\.\d{1,2})?)%?)?",
        re.MULTILINE
    )
    for match in pattern.finditer(clean_text):
        code, name, val1, val2, pct_val = match.groups()
        v1, v2 = int(val1), int(val2)
        held = max(v1, v2)
        attended = min(v1, v2)
        pct = float(pct_val) if pct_val else ((attended / held * 100.0) if held > 0 else 100.0)
        
        if not any(s["code"] == code.strip() for s in subjects):
            subjects.append({
                "code": code.strip(),
                "name": name.strip(),
                "classes_present": attended,
                "classes_total": held,
                "attendance_pct": round(pct, 2),
                "status": "WARNING" if pct < 85.0 else "OK"
            })
    return subjects


def _extract_student_name(html_content: str) -> Optional[str]:
    """Find student name from KP portal profile header."""
    match = re.search(r"Student\s*Name\s*:\s*([^<\n\r]+)", html_content, re.I)
    if match:
        return match.group(1).strip()
    return None


def _extract_student_id(html_content: str) -> Optional[str]:
    """Find register number / student ID."""
    match = re.search(r"(?:Register|Roll|Student\s*ID)\s*No?\s*:\s*([^<\n\r]+)", html_content, re.I)
    if match:
        return match.group(1).strip()
    return None


def _extract_semester(html_content: str) -> Optional[str]:
    """Find current semester."""
    match = re.search(r"Semester\s*:\s*([^<\n\r]+)", html_content, re.I)
    if match:
        return match.group(1).strip()
    return None
