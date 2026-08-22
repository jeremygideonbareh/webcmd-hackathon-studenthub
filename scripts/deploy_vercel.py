"""Deploy Atlas to Vercel via the REST API (CLI token validation is broken on this machine).

Uploads api/ + public/ + vercel.json as a deployment, polls until ready.
"""
import base64
import hashlib
import json
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

TOKEN = sys.argv[1]
TEAM = "team_CIPs8SFDGc0dWNEi1eb6oIqi"
PROJECT = "atlas-studenthub"
ROOT = Path(__file__).resolve().parent.parent
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"


def call(method, url, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        url, data=data, method=method,
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "User-Agent": UA,
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
    )
    try:
        resp = urllib.request.urlopen(req, timeout=60)
        return resp.status, json.loads(resp.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode() or "{}")


def collect_files():
    files = []
    include = ["api", "public", "vercel.json"]
    for name in include:
        p = ROOT / name
        if not p.exists():
            continue
        if p.is_file():
            files.append(p)
        else:
            files.extend(f for f in p.rglob("*") if f.is_file())
    result = []
    for f in sorted(files, key=lambda x: x.as_posix()):
        rel = f.relative_to(ROOT).as_posix().replace("\\", "/")
        result.append({"file": rel, "data": base64.b64encode(f.read_bytes()).decode()})
    return result


def main():
    files = collect_files()
    print(f"uploading {len(files)} files")
    payload = {
        "name": PROJECT,
        "project": PROJECT,
        "files": files,
        "target": "production",
        "projectSettings": {
            "framework": None,
            "buildCommand": None,
            "outputDirectory": None,
            "installCommand": None,
            "devCommand": None,
            "rootDirectory": None,
        },
    }
    status, resp = call("POST", f"https://api.vercel.com/v13/deployments?teamId={TEAM}", payload)
    print("create:", status)
    if status not in (200, 201):
        print(json.dumps(resp)[:800])
        sys.exit(1)
    url = resp.get("url")
    dep_id = resp.get("id")
    print("deployment url:", url)
    print("deployment id:", dep_id)

    # poll ready state
    for _ in range(60):
        time.sleep(5)
        s, r = call("GET", f"https://api.vercel.com/v13/deployments/{dep_id}?teamId={TEAM}")
        state = r.get("readyState")
        print("state:", state)
        if state in ("READY", "ERROR", "CANCELED", "ERRORED"):
            if state != "READY":
                for b in r.get("buildingAt", []) if isinstance(r.get("buildingAt"), list) else []:
                    pass
                print(json.dumps(r.get("error", {}))[:500])
            print("FINAL_URL", f"https://{url}")
            return 0 if state == "READY" else 1
    print("TIMEOUT waiting for deployment")
    return 1


if __name__ == "__main__":
    sys.exit(main())