"""Repro the /api/feedback 502 — show the error body."""
import json
import urllib.request
import urllib.error

payload = {"item_type": "job", "item_id": "internshala_12345", "reaction": "👍"}
req = urllib.request.Request(
    "https://webcmd-hackathon-studenthub.vercel.app/api/feedback",
    data=json.dumps(payload).encode(),
    method="POST",
    headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
)
try:
    with urllib.request.urlopen(req, timeout=30) as r:
        print("OK", r.status, r.read().decode()[:500])
except urllib.error.HTTPError as e:
    print("HTTP", e.code)
    print(e.read().decode()[:800])