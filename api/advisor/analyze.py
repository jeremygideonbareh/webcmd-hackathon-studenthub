"""
Vercel serverless — /api/advisor/analyze
Handles GET, POST, and OPTIONS requests for skill gap analysis.
"""

import json
import os
import sys
from http.server import BaseHTTPRequestHandler

# Add repo root to sys.path for importing intelligence module
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from intelligence import analyze_resume_skills


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        self._process_request(is_post=False)

    def do_POST(self):
        self._process_request(is_post=True)

    def _process_request(self, is_post: bool):
        try:
            skills = ["Python", "Git", "SQL"]
            stream = "Engineering"

            if is_post:
                length = int(self.headers.get("Content-Length", 0))
                if length > 0:
                    body = json.loads(self.rfile.read(length).decode("utf-8"))
                    skills = body.get("skills", skills)
                    stream = body.get("stream", stream)
            else:
                import urllib.parse
                parsed = urllib.parse.urlparse(self.path)
                params = urllib.parse.parse_qs(parsed.query)
                if "skills" in params:
                    skills = [s.strip() for s in params["skills"][0].split(",") if s.strip()]
                if "stream" in params:
                    stream = params["stream"][0]

            result = analyze_resume_skills(user_skills=skills, stream=stream)
            res_bytes = json.dumps(result).encode("utf-8")

            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(res_bytes)))
            self.end_headers()
            self.wfile.write(res_bytes)
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
