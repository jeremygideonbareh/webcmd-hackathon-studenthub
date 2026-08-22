"""
Vercel serverless — /api/chat
Handles POST and OPTIONS for AI Chatbot advisor replies with Groq LPU fallback.
"""

import json
import os
import sys
import urllib.request
from http.server import BaseHTTPRequestHandler

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from intelligence import analyze_resume_skills


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
            user_msg = body.get("message", "").strip()
            stream = body.get("stream", "Engineering")
            user_skills = body.get("user_skills", ["Python", "Git", "SQL"])
            gpa = float(body.get("gpa", 8.2))
            user_groq_key = body.get("groq_api_key") or os.getenv("GROQ_API_KEY")

            analysis = analyze_resume_skills(user_skills=user_skills, stream=stream, groq_api_key=user_groq_key)
            missing = ", ".join(analysis.get("missing_critical_skills", []))
            matched = ", ".join(analysis.get("matched_skills", []))
            score = analysis.get("readiness_score", 70)

            reply = None
            llm_engine = "Atlas AI Core Engine"

            if user_groq_key:
                try:
                    url = "https://api.groq.com/openai/v1/chat/completions"
                    prompt = (
                        f"You are Atlas AI, an expert academic and career advisor for university students in {stream}.\n"
                        f"Student Profile:\n- Matched Skills: {matched}\n- Missing Skills: {missing}\n- CGPA: {gpa}\n\n"
                        f"Student Question: {user_msg}\n\n"
                        f"Provide a concise, encouraging, and actionable response in 2-3 sentences."
                    )
                    payload = json.dumps({
                        "model": "groq/compound",
                        "messages": [{"role": "system", "content": "You are Atlas AI Advisor."}, {"role": "user", "content": prompt}],
                        "max_tokens": 200,
                        "temperature": 0.6
                    }).encode("utf-8")
                    req = urllib.request.Request(
                        url,
                        data=payload,
                        headers={
                            "Content-Type": "application/json",
                            "Authorization": f"Bearer {user_groq_key}",
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                        }
                    )
                    with urllib.request.urlopen(req, timeout=4.0) as resp:
                        gdata = json.loads(resp.read().decode("utf-8"))
                        gchoices = gdata.get("choices", [])
                        if gchoices:
                            reply = gchoices[0].get("message", {}).get("content")
                            llm_engine = "Groq LPU (groq/compound)"
                except Exception as err:
                    print(f"[api/chat.py] Groq error: {err}")

            if not reply:
                msg_lower = user_msg.lower()
                if "resume" in msg_lower or "improve" in msg_lower:
                    bullets = analysis.get("resume_bullet_suggestions", [])
                    top_bullet = bullets[0] if bullets else "Added quantitative project metrics."
                    reply = (
                        f"For your {stream} profile, your current readiness score is {score}%. "
                        f"To boost your resume, focus on highlighting your matched skills ({matched}). "
                        f"Here is a recommended bullet point to add:\n• {top_bullet}"
                    )
                elif "skill" in msg_lower or "lack" in msg_lower or "missing" in msg_lower:
                    proj_title = analysis['recommended_projects'][0]['title'] if analysis.get('recommended_projects') else 'a targeted portfolio'
                    reply = (
                        f"Based on your target stream ({stream}), you are currently missing: {missing}. "
                        f"Your current matching skills are: {matched}. "
                        f"I recommend working on the '{proj_title}' project to fill these gaps!"
                    )
                else:
                    reply = (
                        f"As your Atlas AI Advisor for {stream}, I analyzed your skills ({matched}). "
                        f"Your readiness score is {score}%. You can improve by picking up {missing}."
                    )

            res_bytes = json.dumps({"reply": reply, "llm_engine": llm_engine, "analysis": analysis}).encode("utf-8")
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
