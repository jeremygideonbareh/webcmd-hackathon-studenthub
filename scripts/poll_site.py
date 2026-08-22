"""Poll the deployed Atlas site until it's live, then verify endpoints."""
import json
import sys
import time
import urllib.request
import urllib.error

BASE = "https://webcmd-hackathon-studenthub.vercel.app"
TIMEOUT_S = int(sys.argv[1]) if len(sys.argv) > 1 else 300
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        return resp.status, resp.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:400]
    except Exception as e:
        return -1, f"{type(e).__name__}: {e}"


start = time.time()
print("waiting for deployment...", flush=True)
while time.time() - start < TIMEOUT_S:
    code, body = get(BASE + "/")
    if code == 200:
        print(f"LIVE after {int(time.time()-start)}s")
        print("GET / ->", code, "| html bytes:", len(body))
        code2, digest = get(BASE + "/api/digest")
        print("GET /api/digest ->", code2)
        if code2 == 200:
            d = json.loads(digest)
            print("jobs:", len(d.get("jobs", [])), "| attendance:", len(d.get("attendance", [])), "| housing:", len(d.get("housing", [])))
            print("weights:", d.get("weights", {}))
        else:
            print("digest body:", digest[:300])
        sys.exit(0)
    print(f"  ...{int(time.time()-start)}s status={code}", flush=True)
    time.sleep(10)

print("TIMEOUT waiting for site")
sys.exit(1)