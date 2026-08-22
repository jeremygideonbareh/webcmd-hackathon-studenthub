# nobroker_housing.py (mock version)
import json

def fetch_listings(locality="Koramangala", city="Bangalore", budget_max=15000, property_type="PG"):
    # Mock data standing in for a live housing feed.
    # Real APIs (NoBroker, 99acres) require short-lived, browser-generated
    # auth tokens that can't be replicated by a lightweight script within
    # a hackathon's scope — documented here for the writeup/pitch.
    mock_listings = [
        {"title": "Girls PG near Koramangala", "description": "Single occupancy, WiFi, food included", "price": 12000, "link": "https://example.com/pg1"},
        {"title": "1BHK Flat in Indiranagar", "description": "Fully furnished, near metro", "price": 18000, "link": "https://example.com/flat1"},
        {"title": "Co-living space in Koramangala", "description": "AC, laundry, near tech park", "price": 14500, "link": "https://example.com/pg2"},
        {"title": "Boys PG in Kanmanike", "description": "Double sharing, home food", "price": 9500, "link": "https://example.com/pg3"},
    ]
    return [l for l in mock_listings if l["price"] <= budget_max]


if __name__ == "__main__":
    results = fetch_listings()
    print(json.dumps(results, indent=2))