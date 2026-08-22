"""
Student Discounts & Perks Catalog Module.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Any

BASE_DIR = Path(__file__).resolve().parent.parent


def get_discounts(category: str | None = None, stream: str | None = None) -> List[Dict[str, Any]]:
    """Retrieve student discounts filtered by category or stream."""
    mock_file = BASE_DIR / "data" / "mock" / "discounts.json"
    if not mock_file.exists():
        return []

    try:
        data = json.loads(mock_file.read_text(encoding="utf-8"))
        all_discounts = data.get("discounts", [])

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
    except Exception as err:
        print(f"[discounts] Error reading discounts dataset: {err}")
        return []
