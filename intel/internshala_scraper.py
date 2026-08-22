# internshala_scraper.py
from curl_cffi import requests as curl_requests
from bs4 import BeautifulSoup
import json

def fetch_internships(category="python-internship", location="", stipend_min=0):
    url = f"https://internshala.com/internships/{category}"
    if location:
        url += f"-in-{location}"

    session = curl_requests.Session(impersonate="chrome")
    response = session.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    listings = []
    for card in soup.select(".individual_internship"):
        title_el = card.select_one("a#job_title")
        company_el = card.select_one(".company-name")
        stipend_el = card.select_one(".stipend")

        skills = [tag.get_text(strip=True) for tag in card.select(".job_skill")]

        listings.append({
            "title": title_el.get_text(strip=True) if title_el else "",
            "company": company_el.get_text(strip=True) if company_el else "",
            "description": " ".join(skills),
            "skills": skills,
            "stipend": stipend_el.get_text(strip=True) if stipend_el else "",
            # href is already a full URL here, no prefix needed
            "link": ("https://internshala.com" + title_el["href"]) if title_el and title_el.get("href") else "",
        })

    return listings


if __name__ == "__main__":
    results = fetch_internships(category="python-internship")
    print(f"Found {len(results)} internships")
    print(json.dumps(results[:3], indent=2))