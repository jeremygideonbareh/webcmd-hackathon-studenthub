"""
Atlas Portal Subsystem API.

Provides clean interfaces for Jeremy's orchestrator and Sapna's intelligence layer:
- get_attendance(config, use_mock) -> attendance.json contract
- get_risk_report(attendance_data, threshold) -> risk_report.json contract
- get_gpa(config, use_mock) -> gpa.json contract
"""

import json
import os
from typing import Any, Dict, Optional

from portal.attendance_calculus import (
    calculate_subject_risk,
    generate_risk_report,
)
from portal.attendance_extractor import parse_attendance_html
from portal.gpa_extractor import compute_gpa_trend, parse_gpa_html
from portal.webcmd_adapter import WebCMDAdapter

# Alias for backward compatibility
calculate_risk = calculate_subject_risk

__all__ = [
    "WebCMDAdapter",
    "get_attendance",
    "get_risk_report",
    "get_gpa",
    "calculate_risk",
    "calculate_subject_risk",
    "generate_risk_report",
    "parse_attendance_html",
    "parse_gpa_html",
    "compute_gpa_trend",
]


def get_attendance(
    config: Optional[Dict[str, Any]] = None,
    use_mock: bool = False
) -> Dict[str, Any]:
    """
    Retrieve student attendance from Knowledge Pro portal.

    Args:
        config: Optional configuration dictionary.
        use_mock: If True, immediately load from data/mock/attendance.json.

    Returns:
        Structured dictionary matching attendance.json contract.
    """
    if use_mock:
        mock_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "mock", "attendance.json")
        if os.path.exists(mock_path):
            with open(mock_path, "r", encoding="utf-8") as f:
                return json.load(f)

    try:
        adapter = WebCMDAdapter(config)
        return adapter.scrape_attendance(use_mock_fallback=True)
    except Exception as e:
        print(f"[portal] Error in WebCMD adapter ({e}), using mock attendance fallback")
        mock_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "mock", "attendance.json")
        if os.path.exists(mock_path):
            with open(mock_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"student_id": "22BCE1234", "subjects": []}


def get_risk_report(
    attendance_data: Optional[Dict[str, Any]] = None,
    config: Optional[Dict[str, Any]] = None,
    threshold: float = 0.85,
    use_mock: bool = False
) -> Dict[str, Any]:
    """
    Compute attendance risk analysis and projection for all enrolled subjects.

    Args:
        attendance_data: Optional pre-scraped attendance dictionary.
                         If None, calls get_attendance().
        config: Optional configuration dictionary.
        threshold: Minimum attendance threshold (default 0.85 = 85%).
        use_mock: If True, uses mock attendance if none provided.

    Returns:
        Structured dictionary matching risk_report.json contract.
    """
    if attendance_data is None:
        attendance_data = get_attendance(config=config, use_mock=use_mock)

    return generate_risk_report(attendance_data, threshold=threshold)


def get_gpa(
    config: Optional[Dict[str, Any]] = None,
    use_mock: bool = False
) -> Dict[str, Any]:
    """
    Retrieve student GPA (CGPA and SGPA) and historical trend.

    Args:
        config: Optional configuration dictionary.
        use_mock: If True, immediately load from data/mock/gpa.json.

    Returns:
        Structured dictionary matching gpa.json contract.
    """
    if use_mock:
        mock_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "mock", "gpa.json")
        if os.path.exists(mock_path):
            with open(mock_path, "r", encoding="utf-8") as f:
                return json.load(f)

    try:
        adapter = WebCMDAdapter(config)
        return adapter.scrape_gpa(use_mock_fallback=True)
    except Exception as e:
        print(f"[portal] Error in WebCMD adapter ({e}), using mock GPA fallback")
        mock_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "mock", "gpa.json")
        if os.path.exists(mock_path):
            with open(mock_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"current_cgpa": 8.45, "semester_gpa": 8.72, "gpa_trend": "stable"}
