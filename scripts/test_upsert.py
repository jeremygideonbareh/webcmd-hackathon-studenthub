"""Local test of the upsert fix against real Supabase."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from delivery.supabase_store import SupabaseStore

s = SupabaseStore()
print("ready:", s.ready)
w1 = s.apply_reaction("job", "internshala_12345", "👍")
print("after 1st like:", w1)
w2 = s.apply_reaction("job", "internshala_12345", "👍")
print("after 2nd like:", w2)
assert w2.get("job", 1.0) > w1.get("job", 1.0), "weight should have increased"
print("UPSERT FIX VERIFIED")