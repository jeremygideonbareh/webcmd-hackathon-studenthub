"""Tests for orchestrator.py — pipeline that ties portal + intelligence + delivery."""

import shutil

import pytest

from config import Config
from delivery.database import Database
from delivery.learning_engine import LearningEngine
import orchestrator

REAL_MOCK = orchestrator.BASE_DIR / "data" / "mock"
CONTRACT_FILES = (
    "attendance.json",
    "risk_report.json",
    "gpa.json",
    "filtered_jobs.json",
    "housing_raw.json",
)


def _stage_mock(data_dir):
    data_dir.mkdir(parents=True, exist_ok=True)
    for f in CONTRACT_FILES:
        shutil.copy(REAL_MOCK / f, data_dir / f)


def test_build_digest_from_mock(tmp_path):
    _stage_mock(tmp_path)
    cfg = Config(data_dir=tmp_path, mock_dir=tmp_path, db_path=tmp_path / "test.db")
    digest = orchestrator.build_digest(cfg)
    assert len(digest["attendance"]) == 4
    assert len(digest["jobs"]) == 4
    assert len(digest["housing"]) == 3
    assert digest["gpa"]["current_cgpa"] == 8.45


def test_build_digest_graceful_empty(tmp_path):
    cfg = Config(data_dir=tmp_path, mock_dir=tmp_path, db_path=tmp_path / "test.db")
    digest = orchestrator.build_digest(cfg)
    assert digest["attendance"] == []
    assert digest["jobs"] == []
    assert digest["housing"] == []


def test_run_pipeline_mock_mode(tmp_path):
    _stage_mock(tmp_path)
    cfg = Config(data_dir=tmp_path, mock_dir=tmp_path, db_path=tmp_path / "test.db")
    result = orchestrator.run_pipeline(cfg, mode="mock")
    assert result["status"] == "ok"
    assert len(result["jobs"]) == 4
    assert cfg.db_path.exists()


def test_feedback_weights_persist(tmp_path):
    cfg = Config(data_dir=tmp_path, mock_dir=tmp_path, db_path=tmp_path / "test.db")
    db = Database(db_path=cfg.db_path)
    LearningEngine(db).process_reaction("m1", "job", "internshala_12345", "👍")
    assert db.get_weight("job") > 1.0
    assert db.get_all_weights()["job"] == pytest.approx(1.2)