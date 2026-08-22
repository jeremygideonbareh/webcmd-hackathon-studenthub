"""
Knowledge Pro Student Portal - Public API Facade.

Provides clean interfaces for:
- get_attendance(config, use_mock) -> attendance.json contract
- get_risk_report(attendance_data, threshold) -> risk_report.json contract
- get_gpa(config, use_mock) -> gpa.json contract
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from portal.attendance_calculus import generate_risk_report
from portal.attendance_extractor import parse_attendance_html
from portal.gpa_extractor import parse_gpa_html
from portal.client import KPPortalClient, login_kp_portal


__all__ = [
    "get_attendance",
    "get_risk_report",
    "get_gpa",
    "parse_attendance_html",
    "parse_gpa_html",
    "generate_risk_report",
    "KPPortalClient",
    "login_kp_portal",
]


# Mock data path
MOCK_DATA_DIR = Path(__file__).parent.parent / "data" / "mock"


def _load_mock_data(filename: str) -> Dict[str, Any]:
    """Load mock data from JSON file."""
    mock_path = MOCK_DATA_DIR / filename
    if mock_path.exists():
        with open(mock_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def get_attendance(
    config: Optional[Dict[str, Any]] = None,
    use_mock: bool = False
) -> Dict[str, Any]:
    """
    Retrieve student attendance from Knowledge Pro portal.

    Args:
        config: Optional configuration dictionary with username/password.
        use_mock: If True, immediately load from data/mock/attendance.json.

    Returns:
        Structured dictionary matching attendance.json contract.
    """
    if use_mock:
        return _load_mock_data("attendance.json")
    
    # Use config or environment variables
    username = config.get("username") if config else os.getenv("KP_USERNAME")
    password = config.get("password") if config else os.getenv("KP_PASSWORD")
    
    if not username or not password:
        raise ValueError("KP_USERNAME and KP_PASSWORD required for live scraping")
    
    client = login_kp_portal(username, password)
    try:
        html = client.get_attendance_page()
        return parse_attendance_html(html)
    finally:
        client.logout()


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
    Retrieve student GPA (CGPA and SGPA) from Knowledge Pro portal.

    Args:
        config: Optional configuration dictionary with username/password.
        use_mock: If True, immediately load from data/mock/gpa.json.

    Returns:
        Structured dictionary matching gpa.json contract.
    """
    if use_mock:
        return _load_mock_data("gpa.json")
    
    username = config.get("username") if config else os.getenv("KP_USERNAME")
    password = config.get("password") if config else os.getenv("KP_PASSWORD")
    
    if not username or not password:
        raise ValueError("KP_USERNAME and KP_PASSWORD required for live scraping")
    
    client = login_kp_portal(username, password)
    try:
        html = client.get_gpa_page()
        return parse_gpa_html(html, student_id=username)
    finally:
        client.logout()