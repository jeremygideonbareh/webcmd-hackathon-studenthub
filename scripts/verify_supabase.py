"""Dev check — read current_digest from Supabase via the store module."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from delivery.supabase_store import SupabaseStore  # noqa: E402

store = SupabaseStore()
if not store.ready:
    print("STORE NOT READY — missing env")
    raise SystemExit(1)

rows = store._request("GET", "current_digest?select=digest_type,payload_json")
print("digest rows:", len(rows))
if rows:
    p = rows[0]["payload_json"]
    print("jobs:", len(p.get("jobs", [])), "| attendance:", len(p.get("attendance", [])), "| housing:", len(p.get("housing", [])))

w = store.get_weights()
print("weights:", w)
print("SUPABASE VERIFY PASSED")