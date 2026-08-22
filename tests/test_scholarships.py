"""
Unit tests for intelligence/scholarships.py and intelligence/discounts.py.
"""

from intelligence.discounts import get_discounts
from intelligence.scholarships import get_scholarships


def test_get_scholarships_filtering():
    items = get_scholarships(gpa=8.2, stream="Engineering")
    assert isinstance(items, list)
    assert len(items) > 0
    for s in items:
        assert s["min_gpa"] <= 8.2


def test_get_discounts_filtering():
    items = get_discounts(category="Developer Tools")
    assert isinstance(items, list)
    assert len(items) > 0
    for d in items:
        assert "Developer Tools" in d["category"] or len(items) > 0
