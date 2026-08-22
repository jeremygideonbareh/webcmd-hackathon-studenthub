"""
Vercel serverless — GET /api/digest
Returns the latest digest + preference weights from Supabase.
stdlib only (no framework) for fast, reliable cold starts.
"""

import json
import os
from http.server import BaseHTTPRequestHandler

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")


def _get(path):
    import urllib.request

    req = urllib.request.Request(
        f"{SUPABASE_URL}/rest/v1/{path}",
        headers={
            "apikey": SERVICE_KEY,
            "Authorization": f"Bearer {SERVICE_KEY}",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode())


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            digests = _get("current_digest?digest_type=eq.full&select=payload_json&limit=1")
            weights_rows = _get("preference_weights?select=category,weight")
            payload = digests[0]["payload_json"] if digests else {}
            weights = {r["category"]: r["weight"] for r in weights_rows}
            payload["weights"] = weights
            body = json.dumps(payload).encode()
            self.send_response(200)
            self.send_header("content-type", "application/json")
            self.send_header("content-length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except Exception as e:  # noqa: BLE001 — always return JSON to the client
            self.send_response(502)
            self.send_header("content-type", "application/json")
            body = json.dumps({"error": str(e)}).encode()
            self.send_header("content-length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    def log_message(self, *args):
        pass