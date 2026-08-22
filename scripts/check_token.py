"""Dev check — verify Supabase Management API access token works."""
import json
import sys
import urllib.request
import urllib.error

TOKEN = sys.argv[1]
ENDPOINT = sys.argv[2] if len(sys.argv) > 2 else "https://api.supabase.com/v1/organizations"

req = urllib.request.Request(
    ENDPOINT,
    headers={
        "Authorization": f"Bearer {TOKEN}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "application/json",
    },
)
try:
    resp = urllib.request.urlopen(req, timeout=30)
    print("STATUS", resp.status)
    print(resp.read().decode()[:1000])
except urllib.error.HTTPError as e:
    print("HTTP ERROR", e.code)
    print(e.read().decode()[:500])
except Exception as e:
    print("EXC", type(e).__name__, e)