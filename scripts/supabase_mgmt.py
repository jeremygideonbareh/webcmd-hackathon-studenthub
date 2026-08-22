"""Dev check — Supabase Management API calls."""
import json
import os
import secrets
import sys
import urllib.request
import urllib.error

TOKEN = sys.argv[1]
ACTION = sys.argv[2] if len(sys.argv) > 2 else "regions"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"


def call(method, url, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "User-Agent": UA,
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
    )
    try:
        resp = urllib.request.urlopen(req, timeout=60)
        return resp.status, resp.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:800]
    except Exception as e:
        return -1, f"{type(e).__name__}: {e}"


BASE = "https://api.supabase.com"

if ACTION == "regions":
    status, body = call("GET", f"{BASE}/v1/projects/regions")
    print("STATUS", status)
    print(body[:2000])
elif ACTION == "create":
    db_pass = secrets.token_urlsafe(24)
    print("DB_PASSWORD", db_pass)
    status, body = call("POST", f"{BASE}/v1/projects", {
        "name": "atlas-studenthub",
        "organization_id": sys.argv[3],
        "db_pass": db_pass,
        "region": "ap-south-1",
        "plan": "free",
    })
    print("STATUS", status)
    print(body[:1500])
elif ACTION == "projects":
    status, body = call("GET", f"{BASE}/v1/projects")
    print("STATUS", status)
    print(body[:2000])
elif ACTION == "keys":
    ref = sys.argv[3]
    status, body = call("GET", f"{BASE}/v1/projects/{ref}/api-keys")
    print("STATUS", status)
    print(body[:2000])
elif ACTION == "get":
    ref = sys.argv[3]
    status, body = call("GET", f"{BASE}/v1/projects/{ref}")
    print("STATUS", status)
    print(body[:1500])
elif ACTION == "sql":
    ref = sys.argv[3]
    query = open(sys.argv[4], encoding="utf-8").read()
    status, body = call("POST", f"{BASE}/v1/projects/{ref}/database/query", {"query": query})
    print("STATUS", status)
    print(body[:2000])