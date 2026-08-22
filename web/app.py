"""
Atlas web dashboard — FastAPI app.

Run: uvicorn web.app:app --reload
Endpoints:
    GET  /                     → static/index.html (dashboard)
    GET  /api/digest           → {attendance, jobs, housing, scholarships, discounts, deadlines, gpa, weights}
    POST /api/feedback         → {item_type, item_id, reaction} → learning engine
    POST /api/advisor/analyze  → {skills, stream} → stream skill gap analysis
    GET  /api/scholarships     → [scholarships]
    GET  /api/discounts        → [discounts]
    GET  /api/deadlines        → [academic_deadlines]
    POST /api/attendance/simulate → {present, total, future_attend, future_miss} → projected attendance
    POST /api/auth/session     → save user session profile
    GET  /api/auth/session      → get current active user session profile
"""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from config import Config
from delivery.database import Database
from delivery.learning_engine import LearningEngine
from intelligence import analyze_resume_skills, get_scholarships, get_discounts
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