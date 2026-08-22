"""
Vercel serverless — /api/portal/sync
Handles POST and OPTIONS for Knowledge Pro Student Portal login sync.
"""

import json
import os
import sys
import zlib
from http.server import BaseHTTPRequestHandler

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from portal.attendance_calculus import generate_risk_report


def _get_personalized_student_data(student_id: str, stream: str = "Engineering"):
    seed = zlib.crc32(student_id.encode("utf-8")) if student_id else 12345

    stream_courses = {
        "Engineering": [
            ("CS2001", "Data Structures & Algorithms"),
            ("CS2004", "Operating Systems & Kernel Architecture"),
            ("EEE1001", "Basic Electrical Engineering"),
            ("MAT1002", "Discrete Mathematics & Linear Algebra"),
            ("CS3002", "Database Management Systems"),
        ],
        "Psychology": [
            ("PSY1001", "Cognitive Psychology & Neuroscience"),
            ("PSY1002", "Behavioral Assessment & Psychometrics"),
            ("PSY1003", "Clinical Research & Methodology"),
            ("PSY1004", "Developmental & Social Psychology"),
            ("STAT101", "Statistical Data Analysis for Psychology"),
        ],
        "BBA": [
            ("BBA1001", "Corporate Financial Accounting"),
            ("BBA1002", "Principles of Marketing & Consumer Behavior"),
            ("BBA1003", "Business Economics & Macro Analysis"),
            ("BBA1004", "Organizational Behavior & HR Management"),
            ("FIN2001", "Financial Modeling & Excel Analytics"),
        ],
        "MBA": [
            ("MBA5001", "Strategic Management & Leadership"),
            ("MBA5002", "Corporate Finance & Capital Structure"),
            ("MBA5003", "Advanced Business Analytics & BI"),
            ("MBA5004", "Global Supply Chain & Operations"),
            ("MKT5001", "Product Strategy & Growth Marketing"),
        ],
    }

    courses = stream_courses.get(stream, stream_courses["Engineering"])
    raw_subjects = []

    for idx, (code, name) in enumerate(courses):
        val = (seed + idx * 17) % 25
        total = 45 + (seed % 10)
        present = max(28, min(total, total - (val % 12)))
        raw_subjects.append({
            "code": code,
            "name": name,
            "classes_present": present,
            "classes_total": total,
            "attendance_pct": round((present / total) * 100.0, 2),
            "status": "OK" if (present / total) >= 0.85 else "WARNING"
        })

    attendance_data = {
        "student_name": f"Student ({student_id})",
        "student_id": student_id,
        "semester": "Fall 2026",
        "scraped_at": "2026-08-22T10:00:00+05:30",
        "subjects": raw_subjects
    }

    risk_data = generate_risk_report(attendance_data, threshold=0.85)

    gpa_val = round(7.5 + ((seed % 21) / 10.0), 2)
    gpa_data = {
        "student_id": student_id,
        "current_cgpa": gpa_val,
        "gpa": gpa_val,
        "semester_gpa": round(min(10.0, gpa_val + 0.2), 2),
        "scraped_at": "2026-08-22T10:00:00+05:30",
        "gpa_trend": "improving" if (seed % 2 == 0) else "stable"
    }

    return attendance_data, risk_data, gpa_data


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length).decode("utf-8")) if length > 0 else {}
            username = body.get("username", "").strip()
            stream = body.get("stream", "Engineering")

            attendance_raw, risk_raw, gpa_raw = _get_personalized_student_data(username or "22BCE1234", stream)

            payload = {
                "ok": True,
                "student_id": username,
                "attendance": attendance_raw,
                "risk_report": risk_raw,
                "gpa": gpa_raw,
            }
            res_bytes = json.dumps(payload).encode("utf-8")

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
