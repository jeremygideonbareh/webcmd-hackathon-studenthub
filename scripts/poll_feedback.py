"""Poll /api/feedback until the upsert fix is deployed (no 409)."""
import json
import time
import urllib.request
import urllib.error

BASE = "https://webcmd-hackathon-studenthub.vercel.app"
UA = "Mozilla/5.0"

start = time.time()
for i in range(30):
    payload = {"item_type": "job", "item_id": "internshala_12345", "reaction": "👍"}
    req = urllib.request.Request(
        BASE + "/api/feedback",
        data=json.dumps(payload).encode(),
        method="POST",
        headers={"Content-Type": "application/json", "User-Agent": UA},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            body = json.loads(r.read().decode())
            print(f"[{int(time.time()-start)}s] OK status=200 weights={body.get('weights')}")
            if body.get("ok"):
                print("FEEDBACK FIX DEPLOYED")
                break
    except urllib.error.HTTPError as e:
        err = e.read().decode()[:120]
        print(f"[{int(time.time()-start)}s] HTTP {e.code}: {err}")
    time.sleep(10)