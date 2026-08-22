# integrate.py
import json
from tfidf_matcher import match_resume_to_postings
from internshala_scraper import fetch_internships
from nobroker_housing_mock import fetch_listings

# --- Load your parsed resume ---
with open("resume_parsed.json", "r", encoding="utf-8") as f:
    resume_data = json.load(f)

# ============================================
# PART 1: InternRadar (internships)
# ============================================
internships = fetch_internships(category="python-internship")
top_matches = match_resume_to_postings(resume_data, internships, top_n=5)

internradar_output = {
    "module": "internradar",
    "items": [
        {
            "id": m.get("link", ""),
            "title": m.get("title", ""),
            "detail": f"{m.get('company', '')} — match score {m['match_score']}",
            "url": m.get("link", ""),
            "is_new": True,
        }
        for m in top_matches
    ],
}

with open("internradar_output.json", "w", encoding="utf-8") as f:
    json.dump(internradar_output, f, indent=2)

# ============================================
# PART 2: RentWatch (housing, mock data for now)
# ============================================
housing_listings = fetch_listings(locality="Koramangala", city="Bangalore", budget_max=15000)

rentwatch_output = {
    "module": "rentwatch",
    "items": [
        {
            "id": h.get("link", ""),
            "title": h.get("title", ""),
            "detail": f"₹{h.get('price', '')}/month — {h.get('description', '')}",
            "url": h.get("link", ""),
            "is_new": True,
        }
        for h in housing_listings
    ],
}

with open("rentwatch_output.json", "w", encoding="utf-8") as f:
    json.dump(rentwatch_output, f, indent=2)

# ============================================
# Print both for a quick sanity check
# ============================================
print("=== INTERNRADAR OUTPUT ===")
print(json.dumps(internradar_output, indent=2))
print("\nSaved to internradar_output.json")

print("\n=== RENTWATCH OUTPUT ===")
print(json.dumps(rentwatch_output, indent=2))
print("\nSaved to rentwatch_output.json")