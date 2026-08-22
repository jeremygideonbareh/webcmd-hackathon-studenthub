"""Tests for delivery/learning_engine.py — reaction → weight update engine."""

import pytest

from delivery.database import Database
from delivery.learning_engine import LearningEngine


@pytest.fixture()
def engine(tmp_path):
    db = Database(db_path=tmp_path / "test_atlas.db")
    return LearningEngine(db)


def test_positive_reaction_boosts_weight(engine):
    engine.process_reaction("m1", "job", "internshala_12345", "👍")
    assert engine.get_all_weights()["job"] == pytest.approx(1.2)


def test_negative_reaction_suppresses_weight(engine):
    engine.process_reaction("m1", "job", "internshala_12345", "👎")
    assert engine.get_all_weights()["job"] == pytest.approx(0.8)


def test_star_boost(engine):
    engine.process_reaction("m1", "job", "internshala_12345", "⭐")
    assert engine.get_all_weights()["job"] == pytest.approx(1.5)


def test_block_suppresses_hard(engine):
    engine.process_reaction("m1", "job", "internshala_12345", "🚫")
    assert engine.get_all_weights()["job"] == pytest.approx(0.3)


def test_weights_clamped_upper_bound(engine):
    for _ in range(10):
        engine.process_reaction("m1", "job", "internshala_12345", "⭐")
    weights = engine.get_all_weights()
    assert weights["job"] <= 3.0


def test_weights_clamped_lower_bound(engine):
    for _ in range(10):
        engine.process_reaction("m1", "job", "internshala_12345", "🚫")
    weights = engine.get_all_weights()
    assert weights["job"] >= 0.1


def test_unknown_reaction_no_change(engine):
    engine.process_reaction("m1", "job", "internshala_12345", "🤔")
    assert engine.get_all_weights() == {}


def test_category_extraction_from_item(engine, tmp_path):
    db = Database(db_path=tmp_path / "test_atlas.db")
    db.log_digest("full", '{"jobs": [{"id": "internshala_12345", "categories": ["python_jobs", "remote"]}]}')
    engine = LearningEngine(db)
    engine.process_reaction("m1", "job", "internshala_12345", "👍")
    weights = engine.get_all_weights()
    assert weights["python_jobs"] == pytest.approx(1.2)
    assert weights["remote"] == pytest.approx(1.2)


def test_process_reaction_logs_reaction(engine):
    engine.process_reaction("m1", "job", "internshala_12345", "👍")
    reactions = engine.db.get_reactions()
    assert len(reactions) == 1
    assert reactions[0]["reaction"] == "👍"