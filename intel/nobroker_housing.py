# nobroker_housing.py
import requests
import json

# TODO: replace this with the real endpoint URL you find in
# Chrome DevTools -> Network tab while searching on nobroker.in
NOBROKER_SEARCH_URL = "https://www.99acres.com/api-aggregator/discovery/local-area-config?city=20&resCom=R&preference=S&propertyTypes=1%2C4%2C2%2C3%2C90%2C5%2C22%2C80&module=HP_DESKTOP_SF"  
def fetch_listings(locality="Koramangala", city="Bangalore", budget_max=15000, property_type="PG"):
    # TODO: adjust these params to match whatever the real request in DevTools sends
    params = {
        "locality": locality,
        "city": city,
        "maxRent": budget_max,
        "propertyType": property_type,
    }

    headers = {
        "User-Agent": "Mozilla/5.0",   # real requests usually need a browser-like User-Agent
        "Accept": "application/json",
    }

    response = requests.get(NOBROKER_SEARCH_URL, params=params, headers=headers)
    response.raise_for_status()
    data = response.json()

    # TODO: adjust field names once you see the real JSON shape from DevTools
    listings = []
    for item in data.get("results", []):
        listings.append({
            "title": item.get("propertyTitle", ""),
            "description": f"{item.get('bhk', '')} BHK in {item.get('locality', '')}",
            "price": item.get("rent"),
            "link": item.get("propertyUrl"),
        })

    return listings


# --- Fallback: HTML scraping if no clean JSON endpoint is found ---
from bs4 import BeautifulSoup

def fetch_listings_html_fallback(search_url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(search_url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    listings = []
    # TODO: these CSS selectors are placeholders — inspect the real page's
    # HTML (right-click a listing -> Inspect) and adjust the class names
    for card in soup.select(".propertyCard"):
        title_el = card.select_one(".propertyTitle")
        price_el = card.select_one(".rentAmount")
        link_el = card.select_one("a")

        listings.append({
            "title": title_el.get_text(strip=True) if title_el else "",
            "description": "",
            "price": price_el.get_text(strip=True) if price_el else "",
            "link": link_el["href"] if link_el else "",
        })

    return listings


if __name__ == "__main__":
    try:
        results = fetch_listings()
        print(json.dumps(results, indent=2))
    except Exception as e:
        print("Direct API approach failed, likely needs a real endpoint URL:", e)