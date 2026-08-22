"""End-to-end live verification against the deployed Vercel site."""
import json
import sys
import urllib.request
import urllib.error

BASE = "https://webcmd-hackathon-studenthub.vercel.app"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.status, r.read().decode()


def post(url, payload):
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        method="POST",
        headers={"User-Agent": UA, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.status, r.read().decode()


print("== 1. dashboard ==")
code, body = get(BASE + "/")
print(f"GET / -> {code}, {len(body)} bytes")

print("== 2. digest ==")
code, body = get(BASE + "/api/digest")
d = json.loads(body)
print(f"GET /api/digest -> {code}")
print(f"  jobs={len(d['jobs'])} attendance={len(d['attendance'])} housing={len(d['housing'])}")
print(f"  gpa={d.get('gpa', {}).get('current_cgpa')} weights={d.get('weights')}")

print("== 3. feedback POST (like python job) ==")
code, body = post(BASE + "/api/feedback", {"item_type": "job", "item_id": "internshala_12345", "reaction": "👍"})
res = json.loads(body)
print(f"POST /api/feedback -> {code} ok={res.get('ok')}")
print(f"  weights after: {res.get('weights')}")

print("== 4. digest again (weights should persist) ==")
code, body = get(BASE + "/api/digest")
d2 = json.loads(body)
print(f"  weights now: {d2.get('weights')}")
assert d2.get("weights"), "FAIL: weights not persisted"
print("E2E LIVE VERIFICATION PASSED")