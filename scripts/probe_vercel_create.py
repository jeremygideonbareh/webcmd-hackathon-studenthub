"""Probe Vercel project creation + deployment with/without team scope."""
import json
import sys
import urllib.request
import urllib.error

TOKEN = sys.argv[1]
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"


def call(method, url, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        url, data=data, method=method,
        headers={"Authorization": f"Bearer {TOKEN}", "User-Agent": UA, "Accept": "application/json", "Content-Type": "application/json"},
    )
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        return resp.status, resp.read().decode()[:600]
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:400]
    except Exception as e:
        return -1, f"{type(e).__name__}: {e}"


print("== create project (no team) ==")
print(call("POST", "https://api.vercel.com/v10/projects", {"name": "atlas-studenthub", "framework": None}))
print("== create project (with default team) ==")
print(call("POST", "https://api.vercel.com/v10/projects?teamId=team_CIPs8SFDGc0dWNEi1eb6oIqi", {"name": "atlas-studenthub"}))