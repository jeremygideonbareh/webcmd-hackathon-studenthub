"""
Atlas web dashboard — FastAPI app.

Run: uvicorn web.app:app --reload
Endpoints:
    GET  /                     → static/index.html (dashboard)
    GET  /api/digest           → {attendance, jobs, housing, scholarships, discounts, deadlines, gpa, weights}
    POST /api/feedback         → {item_type, item_id, reaction} → learning engine
    POST /api/advisor/analyze  → {skills, stream} → stream skill gap analysis
    POST /api/chat             → {message, stream, user_skills, gpa, groq_api_key} → interactive AI Chatbot advisor reply
    GET  /api/scholarships     → [scholarships]
    GET  /api/discounts        → [discounts]
    GET  /api/deadlines        → [academic_deadlines]
    POST /api/attendance/simulate → {present, total, future_attend, future_miss} → projected attendance
    POST /api/auth/session     → save user session profile
    GET  /api/auth/session      → get current active user session profile
    POST /api/live/search      → execute real-time WebCMD scraping based on student details
"""

from __future__ import annotations

import json
import os
import urllib.request
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from config import Config
from delivery.database import Database
from delivery.learning_engine import LearningEngine
from intelligence import analyze_resume_skills, execute_live_student_search, get_scholarships, get_discounts
from portal.attendance_calculus import simulate_attendance

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "data"
MOCK_DIR = BASE_DIR.parent / "data" / "mock"
DEFAULT_DB = BASE_DIR.parent / "atlas.db"

app = FastAPI(title="Atlas API")
if (BASE_DIR / "static").exists():
    app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


def _load(name: str) -> dict | list:
    path = DATA_DIR / name
    if not path.exists():
        path = MOCK_DIR / name
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _get_db() -> Database:
    return Database(db_path=DEFAULT_DB)


@app.get("/")
def dashboard() -> FileResponse:
    index_path = BASE_DIR / "static" / "index.html"
    if not index_path.exists():
        index_path = BASE_DIR.parent / "frontend" / "dist" / "index.html"
    return FileResponse(index_path)


@app.get("/api/digest")
def digest() -> dict:
    attendance_raw = _load("attendance.json")
    risk_raw = _load("risk_report.json")
    gpa = _load("gpa.json")
    jobs = _load("filtered_jobs.json")
    housing = _load("housing_raw.json")
    scholarships_raw = _load("scholarships.json")
    discounts_raw = _load("discounts.json")
    deadlines_raw = _load("deadlines.json")
    db = _get_db()
    session = db.get_user_session()

    subjects_by_code = {
        s.get("code"): s.get("name")
        for s in attendance_raw.get("subjects", []) if isinstance(s, dict)
    }
    attendance = []
    for subj in risk_raw.get("subjects", []):
        row = dict(subj)
        row.setdefault("name", subjects_by_code.get(subj.get("code"), "Unknown"))
        attendance.append(row)

    return {
        "attendance": attendance,
        "jobs": jobs.get("jobs", []) if isinstance(jobs, dict) else [],
        "housing": housing.get("listings", []) if isinstance(housing, dict) else [],
        "scholarships": scholarships_raw.get("scholarships", []) if isinstance(scholarships_raw, dict) else [],
        "discounts": discounts_raw.get("discounts", []) if isinstance(discounts_raw, dict) else [],
        "deadlines": deadlines_raw.get("deadlines", []) if isinstance(deadlines_raw, dict) else [],
        "gpa": gpa if isinstance(gpa, dict) else {},
        "user_session": session or {},
        "weights": db.get_all_weights(),
    }


@app.post("/api/live/search")
async def live_search(request: Request) -> JSONResponse:
    """Perform live WebCMD scraping based strictly on student details."""
    body = await request.json()
    stream = body.get("stream", "Engineering")
    gpa = float(body.get("gpa", 8.0))
    locality = body.get("locality", "Koramangala")
    city = body.get("city", "Bangalore")
    skills = body.get("skills", ["Python", "Git", "SQL"])

    results = execute_live_student_search(
        stream=stream,
        gpa=gpa,
        locality=locality,
        city=city,
        skills=skills,
    )
    return JSONResponse(results)


@app.post("/api/chat")
async def chat_advisor(request: Request) -> JSONResponse:
    """Interactive AI Chatbot endpoint answering student resume, skill gap, and academic questions."""
    body = await request.json()
    user_msg = body.get("message", "").strip()
    stream = body.get("stream", "Engineering")
    user_skills = body.get("user_skills", ["Python", "Git", "SQL"])
    gpa = float(body.get("gpa", 8.2))
    user_groq_key = body.get("groq_api_key") or os.getenv("GROQ_API_KEY")

    analysis = analyze_resume_skills(user_skills=user_skills, stream=stream, groq_api_key=user_groq_key)
    missing = ", ".join(analysis.get("missing_critical_skills", []))
    matched = ", ".join(analysis.get("matched_skills", []))
    score = analysis.get("readiness_score", 70)
    engine_type = analysis.get("llm_engine", "Atlas AI Core Engine")

    # If Groq API key is present, query Groq LPU directly for high-speed LLM generation!
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
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                }
            )
            with urllib.request.urlopen(req, timeout=4.0) as resp:
                gdata = json.loads(resp.read().decode("utf-8"))
                gchoices = gdata.get("choices", [])
                if gchoices:
                    greply = gchoices[0].get("message", {}).get("content")
                    return JSONResponse({"reply": greply, "llm_engine": "Groq LPU (groq/compound)", "analysis": analysis})
        except Exception as err:
            print(f"[app.py] Groq chat error: {err}")

    # Fallback response generator
    msg_lower = user_msg.lower()

    if "resume" in msg_lower or "improve" in msg_lower:
        bullets = analysis.get("resume_bullet_suggestions", [])
        top_bullet = bullets[0] if bullets else "Added quantitative project metrics."
        reply = (
            f"For your {stream} profile, your current readiness score is {score}%. "
            f"To boost your resume, focus on highlighting your matched skills ({matched}). "
            f"Here is a recommended bullet point to add:\n• {top_bullet}\n"
            f"Also, build a project targeting your missing critical skills: {missing}."
        )
    elif "skill" in msg_lower or "lack" in msg_lower or "missing" in msg_lower:
        reply = (
            f"Based on your target stream ({stream}), you are currently missing: {missing}. "
            f"Your current matching skills are: {matched}. "
            f"I recommend working on the '{analysis['recommended_projects'][0]['title']}' project to fill these gaps!"
        )
    elif "scholarship" in msg_lower or "gpa" in msg_lower or "grant" in msg_lower:
        scholarships_list = get_scholarships(gpa=gpa, stream=stream)
        top_sch = scholarships_list[0]["name"] if scholarships_list else "National Merit Scholarship"
        reply = (
            f"With a CGPA of {gpa} in {stream}, you qualify for {len(scholarships_list)} scholarships! "
            f"Your top match is: '{top_sch}'. Check out the Scholarships tab to view full details and apply."
        )
    elif "class" in msg_lower or "attend" in msg_lower or "miss" in msg_lower:
        reply = (
            f"For Christ University, attendance must be maintained above 85% to avoid fines and 75% for hall ticket eligibility. "
            f"Use the Class Simulator tab to calculate exactly how many classes you can miss or need to attend!"
        )
    else:
        reply = (
            f"As your Atlas AI Advisor for {stream}, I analyzed your skills ({matched}). "
            f"Your readiness score is {score}%. You can improve by picking up {missing}. "
            f"How else can I help you with internships, scholarships, or housing today?"
        )

    return JSONResponse({"reply": reply, "llm_engine": engine_type, "analysis": analysis})


@app.post("/api/feedback")
async def feedback(request: Request) -> JSONResponse:
    body = await request.json()
    db = _get_db()
    engine = LearningEngine(db)
    engine.process_reaction(
        message_id=str(body.get("item_id", "feedback")),
        item_type=str(body.get("item_type", "item")),
        item_id=str(body.get("item_id", "")),
        reaction=str(body.get("reaction", "")),
    )
    return JSONResponse({"ok": True, "weights": db.get_all_weights()})


@app.post("/api/auth/session")
async def save_session(request: Request) -> JSONResponse:
    body = await request.json()
    email = body.get("email", "student@christuniversity.in")
    university = body.get("university", "Christ University (Knowledge Pro)")
    student_id = body.get("student_id", "")
    stream = body.get("stream", "Engineering")

    db = _get_db()
    saved = db.save_user_session(email=email, university=university, student_id=student_id, stream=stream)
    return JSONResponse({"ok": True, "session": saved})


@app.get("/api/auth/session")
def get_session(email: str | None = None) -> JSONResponse:
    db = _get_db()
    sess = db.get_user_session(email=email)
    return JSONResponse({"session": sess or {}})


@app.post("/api/advisor/analyze")
async def advisor_analyze(request: Request) -> JSONResponse:
    body = await request.json()
    user_skills = body.get("skills", ["Python", "Git", "SQL"])
    stream = body.get("stream", "Engineering")
    result = analyze_resume_skills(user_skills=user_skills, stream=stream)
    return JSONResponse(result)


@app.get("/api/scholarships")
def scholarships(gpa: float = 8.0, stream: str = "Engineering") -> JSONResponse:
    data = get_scholarships(gpa=gpa, stream=stream)
    return JSONResponse({"scholarships": data})


@app.get("/api/discounts")
def discounts(category: str | None = None, stream: str | None = None) -> JSONResponse:
    data = get_discounts(category=category, stream=stream)
    return JSONResponse({"discounts": data})


@app.get("/api/deadlines")
def deadlines() -> JSONResponse:
    data = _load("deadlines.json")
    items = data.get("deadlines", []) if isinstance(data, dict) else []
    return JSONResponse({"deadlines": items})


@app.post("/api/attendance/simulate")
async def attendance_simulate(request: Request) -> JSONResponse:
    body = await request.json()
    present = int(body.get("present", 40))
    total = int(body.get("total", 50))
    future_attend = int(body.get("future_attend", 0))
    future_miss = int(body.get("future_miss", 0))
    result = simulate_attendance(present, total, future_attend=future_attend, future_miss=future_miss)
    return JSONResponse(result)