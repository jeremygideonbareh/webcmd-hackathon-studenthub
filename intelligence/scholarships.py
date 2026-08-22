"""
Scholarships Matcher & Aggregator Module.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Any

BASE_DIR = Path(__file__).resolve().parent.parent


def get_scholarships(gpa: float = 8.0, stream: str = "Engineering") -> List[Dict[str, Any]]:
    """Retrieve scholarships filtered by student GPA and academic stream."""
    mock_file = BASE_DIR / "data" / "mock" / "scholarships.json"
    if not mock_file.exists():
        return []

    try:
        data = json.loads(mock_file.read_text(encoding="utf-8"))
        all_scholarships = data.get("scholarships", [])

        # Filter by GPA eligibility and stream matching
        matching = []
        for s in all_scholarships:
            min_gpa = s.get("min_gpa", 0.0)
            streams = s.get("streams", [])

            if gpa >= min_gpa and (not streams or any(st.lower() in stream.lower() or stream.lower() in st.lower() for st in streams)):
                matching.append(s)

        # Return matching or all fallback if strict filter yields 0
        return matching if matching else all_scholarships[:3]
    except Exception as err:
        print(f"[scholarships] Error reading scholarships dataset: {err}")
        return []
