"""
Atlas web dashboard — FastAPI app.

Run: uvicorn web.app:app --reload
Endpoints:
    GET  /                 → static/index.html (dashboard)
    GET  /api/digest       → {attendance, jobs, housing, gpa, weights}
    POST /api/feedback     → {item_type, item_id, reaction} → learning engine
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

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "data"
DEFAULT_DB = BASE_DIR.parent / "atlas.db"

app = FastAPI(title="Atlas")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


def _load(name: str) -> dict | list:
    path = DATA_DIR / name
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
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.get("/api/digest")
def digest() -> dict:
    attendance_raw = _load("attendance.json")
    risk_raw = _load("risk_report.json")
    gpa = _load("gpa.json")
    jobs = _load("filtered_jobs.json")
    housing = _load("housing_raw.json")
    db = _get_db()

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
        "gpa": gpa if isinstance(gpa, dict) else {},
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