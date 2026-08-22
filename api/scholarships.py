"""
Vercel serverless — /api/scholarships
Returns scholarships filtered by GPA and stream.
"""

import json
import os
import sys
from http.server import BaseHTTPRequestHandler

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from intelligence import get_scholarships


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        try:
            import urllib.parse
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)

            gpa = float(params["gpa"][0]) if "gpa" in params else 7.5
            stream = params["stream"][0] if "stream" in params else "Engineering"

            if stream == "All" or stream == "undefined":
                stream = "Engineering"

            data = get_scholarships(gpa=gpa, stream=stream)
            res_bytes = json.dumps({"scholarships": data}).encode("utf-8")

            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(res_bytes)))
            self.end_headers()
            self.wfile.write(res_bytes)
        except Exception as e:
            err_body = json.dumps({"scholarships": [], "error": str(e)}).encode("utf-8")
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(err_body)))
            self.end_headers()
            self.wfile.write(err_body)

    def log_message(self, *args):
        pass
