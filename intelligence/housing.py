# intelligence/housing.py
"""
Thin wrapper connecting the intel/ housing data source to the
intelligence package's public interface.

NOTE: Currently backed by mock data (see intel/nobroker_housing_mock.py).
Real housing platforms (NoBroker, 99acres) protect their listings behind
short-lived, browser-generated auth tokens that can't be replicated by a
lightweight script within this project's scope — see that module's
comments for details. Swap the import below for a real data source
if one becomes available later without changing this function's signature.
"""

from typing import List, Dict, Any, Optional

try:
    from nobroker_housing_mock import fetch_listings

    _HOUSING_SOURCE_AVAILABLE = True
except ImportError:
    # Prototype script (nobroker_housing_mock.py) lives outside this repo.
    # Keep the package importable; raise only when get_housing() is called.
    _HOUSING_SOURCE_AVAILABLE = False


def get_housing(
    locality: str = "Koramangala",
    city: str = "Bangalore",
    budget_max: int = 15000,
    property_type: Optional[str] = "PG",
) -> List[Dict[str, Any]]:
    """
    Return housing/PG listings matching the given filters.

    Args:
        locality: neighborhood to search within
        city: city to search within
        budget_max: maximum monthly rent in INR
        property_type: e.g. "PG", "Flat" (mock data currently ignores this
                       filter but the parameter is kept for interface
                       compatibility with a future real data source)

    Returns:
        list of listing dicts (title, description, price, link)
    """
    if not _HOUSING_SOURCE_AVAILABLE:
        raise RuntimeError(
            "Housing dependency missing: nobroker_housing_mock.py must be "
            "importable (copy it into the repo or add its folder to "
            "PYTHONPATH)."
        )
    return fetch_listings(locality=locality, city=city, budget_max=budget_max)


if __name__ == "__main__":
    import json
    results = get_housing()
    print(json.dumps(results, indent=2))