"""
Unified Extractor Module for Knowledge Pro Student Portal.

Re-exports attendance and GPA extraction functions for convenience.
"""

from portal.attendance_extractor import parse_attendance_html
from portal.gpa_extractor import parse_gpa_html, compute_gpa_trend

__all__ = [
    "parse_attendance_html",
    "parse_gpa_html", 
    "compute_gpa_trend",
]