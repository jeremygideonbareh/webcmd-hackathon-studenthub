"""Dev check — hit the live dashboard and print digest summary."""
import json
import sys
import urllib.request

base = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8765"

html = urllib.request.urlopen(base + "/").read()
print("GET / ->", len(html), "bytes html")

d = json.loads(urllib.request.urlopen(base + "/api/digest").read())
print("jobs:", len(d["jobs"]), "| attendance:", len(d["attendance"]), "| housing:", len(d["housing"]))
print("gpa:", d["gpa"].get("current_cgpa"))

import urllib.request as r
req = r.Request(
    base + "/api/feedback",
    data=json.dumps({"item_type": "job", "item_id": "internshala_12345", "reaction": "👍"}).encode(),
    headers={"Content-Type": "application/json"},
    method="POST",
)
res = json.loads(r.urlopen(req).read())
print("POST /api/feedback -> ok:", res["ok"], "| weights:", res["weights"])
print("LIVE CHECK PASSED")