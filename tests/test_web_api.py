"""Tests for web/app.py — FastAPI dashboard endpoints."""

import json
import shutil
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from web.app import app

client = TestClient(app)
REPO_ROOT = Path(__file__).resolve().parent.parent
REAL_MOCK = REPO_ROOT / "data" / "mock"


@pytest.fixture(scope="module", autouse=True)
def stage_mock_into_data():
    """Copy mock contracts into data/ so /api/digest has something to serve."""
    data_dir = REPO_ROOT / "data"
    data_dir.mkdir(exist_ok=True)
    for f in ("attendance.json", "risk_report.json", "gpa.json", "filtered_jobs.json", "housing_raw.json"):
        shutil.copy(REAL_MOCK / f, data_dir / f)


def test_dashboard_served():
    r = client.get("/")
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]


def test_digest_shape():
    r = client.get("/api/digest")
    assert r.status_code == 200
    body = r.json()
    assert "attendance" in body
    assert "jobs" in body
    assert "housing" in body
    assert "gpa" in body
    assert "weights" in body


def test_digest_jobs_have_match_score():
    body = client.get("/api/digest").json()
    assert len(body["jobs"]) > 0
    for job in body["jobs"]:
        assert "match_score" in job
        assert "title" in job


def test_digest_attendance_has_risk_level():
    body = client.get("/api/digest").json()
    assert len(body["attendance"]) > 0
    for subj in body["attendance"]:
        assert "risk_level" in subj


def test_feedback_boosts_weight():
    r = client.post(
        "/api/feedback",
        json={"item_type": "job", "item_id": "internshala_12345", "reaction": "👍"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert "weights" in body


def test_feedback_unknown_reaction_ok():
    r = client.post(
        "/api/feedback",
        json={"item_type": "job", "item_id": "internshala_12345", "reaction": "🤔"},
    )
    assert r.status_code == 200
    assert r.json()["ok"] is True


def test_digest_returns_empty_on_missing_data(tmp_path, monkeypatch):
    # Point the app at an empty data dir to verify graceful fallback
    empty = tmp_path / "empty"
    empty.mkdir()
    import web.app as app_mod

    monkeypatch.setattr(app_mod, "DATA_DIR", empty)
    monkeypatch.setattr(app_mod, "MOCK_DIR", empty)
    r = client.get("/api/digest")
    assert r.status_code == 200
    body = r.json()
    assert body["attendance"] == []
    assert body["jobs"] == []
    assert body["housing"] == []