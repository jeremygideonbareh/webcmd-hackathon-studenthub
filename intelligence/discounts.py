# intelligence/discounts.py
"""
Student Deals & Perks Finder.

Returns a curated list of student discounts/perks, filterable by
category and (optionally) relevance to a specific academic stream.
"""

from typing import List, Dict, Any, Optional

# Static dataset of common student deals. In a real deployment this could
# be moved to a JSON file like scholarships.json, but a static list is
# fine for a hackathon scope since these offers change infrequently.

DISCOUNTS: List[Dict[str, Any]] = [
    {
        "name": "GitHub Student Developer Pack",
        "category": "Developer tools",
        "streams": ["Engineering", "MBA"],
        "discount": "Free access to 100+ developer tools",
        "provider": "GitHub Education",
        "link": "https://education.github.com/pack",
    },
    {
        "name": "JetBrains Student License",
        "category": "Developer tools",
        "streams": ["Engineering"],
        "discount": "Free IDE licenses (PyCharm, IntelliJ, etc.)",
        "provider": "JetBrains",
        "link": "https://www.jetbrains.com/community/education/",
    },
    {
        "name": "Notion for Education",
        "category": "Productivity",
        "streams": ["Engineering", "Psychology", "BBA", "MBA"],
        "discount": "Free Notion Plus plan for students",
        "provider": "Notion",
        "link": "https://www.notion.so/students",
    },
    {
        "name": "Microsoft 365 Education",
        "category": "Productivity",
        "streams": ["Engineering", "Psychology", "BBA", "MBA"],
        "discount": "Free Office apps and 5GB OneDrive storage",
        "provider": "Microsoft",
        "link": "https://www.microsoft.com/en-in/education/products/office",
    },
    {
        "name": "SPSS Student Version",
        "category": "Research software",
        "streams": ["Psychology"],
        "discount": "Discounted annual license for students",
        "provider": "IBM",
        "link": "https://www.ibm.com/products/spss-statistics/pricing",
    },
    {
        "name": "Qualtrics Student Account",
        "category": "Research software",
        "streams": ["Psychology"],
        "discount": "Free academic survey account via university partnership",
        "provider": "Qualtrics",
        "link": "https://www.qualtrics.com/university/",
    },
    {
        "name": "Tableau for Students",
        "category": "Research software",
        "streams": ["MBA", "Engineering"],
        "discount": "Free 1-year Tableau Desktop license",
        "provider": "Tableau",
        "link": "https://www.tableau.com/academic/students",
    },
    {
        "name": "Bloomberg Terminal Campus Access",
        "category": "Finance",
        "streams": ["MBA", "BBA"],
        "discount": "On-campus terminal access for finance coursework",
        "provider": "Bloomberg",
        "link": "https://www.bloomberg.com/professional/",
    },
    {
        "name": "Perplexity Pro Student Discount",
        "category": "Subscriptions",
        "streams": ["Engineering", "Psychology", "BBA", "MBA"],
        "discount": "50% off Perplexity Pro for verified students",
        "provider": "Perplexity",
        "link": "https://www.perplexity.ai/",
    },
    {
        "name": "Spotify Student Premium",
        "category": "Subscriptions",
        "streams": ["Engineering", "Psychology", "BBA", "MBA"],
        "discount": "Discounted Premium + Hulu + SHOWTIME bundle",
        "provider": "Spotify",
        "link": "https://www.spotify.com/student/",
    },
    {
        "name": "Amazon Prime Student",
        "category": "Subscriptions",
        "streams": ["Engineering", "Psychology", "BBA", "MBA"],
        "discount": "6-month free trial, then 50% off Prime",
        "provider": "Amazon",
        "link": "https://www.amazon.in/amazonprime/student",
    },
    {
        "name": "Canva Pro for Students",
        "category": "Productivity",
        "streams": ["BBA", "MBA", "Psychology"],
        "discount": "Free Canva Pro for verified students",
        "provider": "Canva",
        "link": "https://www.canva.com/education/",
    },
]


def get_discounts(category: Optional[str] = None, stream: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Return student discounts, optionally filtered by category and/or stream.

    Args:
        category: one of "Developer tools", "Productivity", "Research software",
                  "Finance", "Subscriptions" — or None to include all categories
        stream: one of "Engineering", "Psychology", "BBA", "MBA" — or None
                to include deals for all streams

    Returns:
        list of matching discount dicts
    """
    results = DISCOUNTS

    if category is not None:
        results = [d for d in results if d["category"].lower() == category.lower()]

    if stream is not None:
        results = [d for d in results if stream in d["streams"]]

    return results


if __name__ == "__main__":
    # Quick manual test
    results = get_discounts(stream="Psychology")
    print(f"Found {len(results)} deals for Psychology students:\n")
    for d in results:
        print(f"- {d['name']} ({d['category']}): {d['discount']}")