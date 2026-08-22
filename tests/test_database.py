"""Tests for delivery/database.py — SQLite CRUD operations."""

import json

import pytest

from delivery.database import Database


@pytest.fixture()
def db(tmp_path):
    return Database(db_path=tmp_path / "test_atlas.db")


def test_schema_created(db):
    tables = db.get_tables()
    assert {"reactions", "preference_weights", "digest_history"} <= set(tables)


def test_log_reaction(db):
    rid = db.log_reaction("msg_1", "job", "internshala_12345", "👍")
    assert rid is not None
    rows = db.get_reactions()
    assert len(rows) == 1
    assert rows[0]["item_id"] == "internshala_12345"


def test_get_weight_default_is_1_0(db):
    assert db.get_weight("python_jobs") == 1.0


def test_update_weight_and_get(db):
    db.update_weight("python_jobs", 1.2)
    assert db.get_weight("python_jobs") == 1.2


def test_update_weight_upserts(db):
    db.update_weight("remote", 0.8)
    db.update_weight("remote", 0.9)
    weights = db.get_all_weights()
    assert weights["remote"] == 0.9


def test_get_all_weights_empty(db):
    assert db.get_all_weights() == {}


def test_log_digest(db):
    db.log_digest("full", json.dumps({"jobs": []}))
    history = db.get_digest_history()
    assert len(history) == 1
    assert history[0]["digest_type"] == "full"


def test_get_digest_item_returns_none_when_missing(db):
    assert db.get_digest_item("nonexistent") is None


def test_get_digest_item_returns_json(db):
    db.log_digest("full", json.dumps({"jobs": [{"id": "x", "categories": ["python_jobs"]}]}))
    item = db.get_digest_item("x")
    assert item is not None
    assert item["categories"] == ["python_jobs"]