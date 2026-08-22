"""Dev check — verify Vercel token against the API."""
import sys
import urllib.request
import urllib.error

TOKEN = sys.argv[1]
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

for endpoint in ("https://api.vercel.com/v2/user", "https://api.vercel.com/v2/teams"):
    req = urllib.request.Request(
        endpoint,
        headers={"Authorization": f"Bearer {TOKEN}", "User-Agent": UA, "Accept": "application/json"},
    )
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        print(endpoint.split("/")[-1], "->", resp.status)
        print(resp.read().decode()[:800])
    except urllib.error.HTTPError as e:
        print(endpoint.split("/")[-1], "-> HTTP", e.code)
        print(e.read().decode()[:500])
    except Exception as e:
        print(endpoint.split("/")[-1], "->", type(e).__name__, e)