"""
Vercel serverless — POST /api/feedback
Logs a reaction and applies the learning-engine weight update in Supabase.
Same multipliers + clamping as delivery/learning_engine.py.
stdlib only.
"""

import json
import os
from http.server import BaseHTTPRequestHandler

SUPABASE_URL = os.environ.get("SUPABASE_URL", "").strip()
SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "").strip()

REACTION_MULTIPLIERS = {"👍": 1.2, "👎": 0.8, "⭐": 1.5, "🚫": 0.3}
WEIGHT_MIN, WEIGHT_MAX = 0.1, 3.0


def _request(method, path, payload=None):
    import urllib.request
    import urllib.error

    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(
        f"{SUPABASE_URL}/rest/v1/{path}",
        data=data,
        method=method,
        headers={
            "apikey": SERVICE_KEY,
            "Authorization": f"Bearer {SERVICE_KEY}",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Prefer": "return=representation,resolution=merge-duplicates",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            raw = resp.read().decode()
            return json.loads(raw) if raw else []
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Supabase {e.code}: {e.read().decode()[:300]}") from e


def _get_current_digest():
    rows = _request("GET", "current_digest?digest_type=eq.full&select=payload_json&limit=1")
    return rows[0]["payload_json"] if rows else {}


def _extract_categories(item_type, item_id, digest):
    for section in ("jobs", "housing"):
        for item in digest.get(section, []):
            if str(item.get("id")) == str(item_id):
                cats = item.get("categories")
                if cats:
                    return list(cats)
                skills = item.get("skills_required")
                if skills:
                    return [f"{s.lower()}_jobs" for s in skills]
    return [item_type]


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length).decode() or "{}")
            item_type = str(body.get("item_type", "item"))
            item_id = str(body.get("item_id", ""))
            reaction = str(body.get("reaction", ""))

            multiplier = REACTION_MULTIPLIERS.get(reaction, 1.0)

            # log the reaction
            _request(
                "POST",
                "reactions",
                {"message_id": item_id or "feedback", "item_type": item_type, "item_id": item_id, "reaction": reaction},
            )

            if reaction in REACTION_MULTIPLIERS:
                digest = _get_current_digest()
                categories = _extract_categories(item_type, item_id, digest)
                rows = _request("GET", "preference_weights?select=category,weight")
                weights = {r["category"]: r["weight"] for r in rows}

                for cat in categories:
                    current = weights.get(cat, 1.0)
                    new_weight = max(WEIGHT_MIN, min(WEIGHT_MAX, current * multiplier))
                    # upsert on category
                    _request(
                        "POST",
                        f"preference_weights?on_conflict=category",
                        {"category": cat, "weight": new_weight},
                    )
                    weights[cat] = new_weight

                response = {"ok": True, "weights": weights}
            else:
                response = {"ok": True, "weights": {}}

            body_out = json.dumps(response).encode()
            self.send_response(200)
            self.send_header("content-type", "application/json")
            self.send_header("content-length", str(len(body_out)))
            self.end_headers()
            self.wfile.write(body_out)
        except Exception as e:  # noqa: BLE001
            self.send_response(502)
            self.send_header("content-type", "application/json")
            body_out = json.dumps({"ok": False, "error": str(e)}).encode()
            self.send_header("content-length", str(len(body_out)))
            self.end_headers()
            self.wfile.write(body_out)

    def log_message(self, *args):
        pass