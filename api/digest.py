"""
Vercel serverless — GET /api/digest
Returns the latest digest + preference weights with graceful local fallback.
"""

import json
import os
import sys
from http.server import BaseHTTPRequestHandler

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(REPO_ROOT, "data")

SUPABASE_URL = os.environ.get("SUPABASE_URL", "").strip()
SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "").strip()


def _get_supabase(path):
    import urllib.request
    req = urllib.request.Request(
        f"{SUPABASE_URL}/rest/v1/{path}",
        headers={
            "apikey": SERVICE_KEY,
            "Authorization": f"Bearer {SERVICE_KEY}",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode())


def _read_local_json(filename):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        path = os.path.join(DATA_DIR, "mock", filename)
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        try:
            payload = {}
            if SUPABASE_URL and SERVICE_KEY:
                try:
                    digests = _get_supabase("current_digest?digest_type=eq.full&select=payload_json&limit=1")
                    weights_rows = _get_supabase("preference_weights?select=category,weight")
                    payload = digests[0]["payload_json"] if digests else {}
                    weights = {r["category"]: r["weight"] for r in weights_rows}
                    payload["weights"] = weights
                except Exception:
                    pass

            if not payload:
                risk_raw = _read_local_json("risk_report.json")
                attendance_raw = _read_local_json("attendance.json")
                gpa_raw = _read_local_json("gpa.json")
                jobs_raw = _read_local_json("filtered_jobs.json")
                housing_raw = _read_local_json("housing_raw.json")
                scholarships_raw = _read_local_json("scholarships.json")
                discounts_raw = _read_local_json("discounts.json")
                deadlines_raw = _read_local_json("deadlines.json")

                subjects_by_code = {
                    s.get("code"): s.get("name")
                    for s in attendance_raw.get("subjects", []) if isinstance(s, dict)
                }
                attendance = []
                for subj in risk_raw.get("subjects", []):
                    row = dict(subj)
                    row.setdefault("name", subjects_by_code.get(subj.get("code"), "Unknown"))
                    attendance.append(row)

                payload = {
                    "attendance": attendance,
                    "jobs": jobs_raw.get("jobs", []) if isinstance(jobs_raw, dict) else [],
                    "housing": housing_raw.get("listings", []) if isinstance(housing_raw, dict) else [],
                    "scholarships": scholarships_raw.get("scholarships", []) if isinstance(scholarships_raw, dict) else [],
                    "discounts": discounts_raw.get("discounts", []) if isinstance(discounts_raw, dict) else [],
                    "deadlines": deadlines_raw.get("deadlines", []) if isinstance(deadlines_raw, dict) else [],
                    "gpa": gpa_raw if isinstance(gpa_raw, dict) else {},
                    "weights": {},
                }

            body = json.dumps(payload).encode("utf-8")
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except Exception as e:
            err_body = json.dumps({"error": str(e)}).encode("utf-8")
            self.send_response(500)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(err_body)))
            self.end_headers()
            self.wfile.write(err_body)

    def log_message(self, *args):
        pass