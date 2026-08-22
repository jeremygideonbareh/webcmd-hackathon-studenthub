"""
Student Deals & Perks Catalog Module.

Returns a curated list of student discounts/perks, filterable by
category and/or relevance to a specific academic stream.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

BASE_DIR = Path(__file__).resolve().parent.parent

STATIC_DISCOUNTS: List[Dict[str, Any]] = [
    {
        "id": "disc_static_01",
        "title": "GitHub Student Developer Pack",
        "name": "GitHub Student Developer Pack",
        "category": "Developer Tools",
        "discount": "100% FREE ($200+ Value)",
        "description": "Free access to 100+ developer tools, Copilot, JetBrains, and domain credits.",
        "provider": "GitHub Education",
        "streams": ["Engineering", "MBA", "BBA"],
        "code": "STUDENT-EDU-VERIFY",
        "url": "https://education.github.com/pack",
        "link": "https://education.github.com/pack",
    },
    {
        "id": "disc_static_02",
        "title": "JetBrains Student License",
        "name": "JetBrains Student License",
        "category": "Developer Tools",
        "discount": "100% FREE",
        "description": "Free IDE licenses (PyCharm, IntelliJ IDEA, WebStorm, CLion).",
        "provider": "JetBrains",
        "streams": ["Engineering"],
        "code": "EDU-JETBRAINS-FREE",
        "url": "https://www.jetbrains.com/community/education/",
        "link": "https://www.jetbrains.com/community/education/",
    },
    {
        "id": "disc_static_03",
        "title": "Notion Education Plus Plan",
        "name": "Notion Education Plus Plan",
        "category": "Productivity",
        "discount": "100% FREE",
        "description": "Unlimited blocks, page history, and collaborative workspace for student notes.",
        "provider": "Notion",
        "streams": ["Engineering", "Psychology", "BBA", "MBA"],
        "code": "AUTO-EDU-LOGIN",
        "url": "https://www.notion.so/product/notion-for-education",
        "link": "https://www.notion.so/product/notion-for-education",
    },
    {
        "id": "disc_static_04",
        "title": "IBM SPSS & Qualtrics Student License",
        "name": "IBM SPSS & Qualtrics Student License",
        "category": "Research & Analytics",
        "discount": "80% OFF",
        "description": "Discounted license for IBM SPSS Statistics and Qualtrics survey research tools.",
        "provider": "IBM / Qualtrics",
        "streams": ["Psychology", "MBA"],
        "code": "PSYCH-RESEARCH-80",
        "url": "https://www.ibm.com/analytics/spss-statistics",
        "link": "https://www.ibm.com/analytics/spss-statistics",
    },
    {
        "id": "disc_static_05",
        "title": "Tableau Academic Student License",
        "name": "Tableau Academic Student License",
        "category": "Research & Analytics",
        "discount": "100% FREE",
        "description": "Free 1-year Tableau Desktop license for data visualization and business intelligence.",
        "provider": "Tableau",
        "streams": ["MBA", "Engineering", "BBA"],
        "code": "TABLEAU-STUDENT-FREE",
        "url": "https://www.tableau.com/academic/students",
        "link": "https://www.tableau.com/academic/students",
    },
    {
        "id": "disc_static_06",
        "title": "Spotify Premium + Hulu Student Bundle",
        "name": "Spotify Premium + Hulu Student Bundle",
        "category": "Subscriptions",
        "discount": "50% OFF (₹59/month)",
        "description": "Discounted ad-free music streaming and entertainment package.",
        "provider": "Spotify",
        "streams": ["Engineering", "Psychology", "BBA", "MBA"],
        "code": "SPOTIFY-STUDENT-SHEERID",
        "url": "https://www.spotify.com/student/",
        "link": "https://www.spotify.com/student/",
    },
]


def _load_json_discounts() -> List[Dict[str, Any]]:
    path = BASE_DIR / "data" / "discounts.json"
    if not path.exists():
        path = BASE_DIR / "data" / "mock" / "discounts.json"
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return data.get("discounts", [])
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def get_discounts(category: Optional[str] = None, stream: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve student discounts filtered by category or stream."""
    all_discounts = _load_json_discounts() or STATIC_DISCOUNTS

    if not category and not stream:
        return all_discounts

    filtered = []
    for item in all_discounts:
        cat_match = not category or category.lower() in item.get("category", "").lower()
        streams = item.get("streams", [])
        stream_match = not stream or any(st.lower() in stream.lower() or stream.lower() in st.lower() for st in streams)

        if cat_match and stream_match:
            filtered.append(item)

    return filtered if filtered else all_discounts
