"""
Atlas main pipeline — ties Aaron's portal scraper + Sapna's intelligence
layer + Jeremy's web delivery together.

Modes:
    python orchestrator.py            # mock data (default) — safe, no network
    python orchestrator.py --mock     # same as default
    python orchestrator.py --live     # real portal + intelligence modules
    python orchestrator.py --live-demo  # live but with extra logging for demos

Flow:
    1. Load config
    2. Gather data (mock files, or real portal/intelligence modules)
    3. Load preference weights from SQLite
    4. Build digest payload
    5. Write digest to data/*.json (dashboard reads these live)
    6. Log digest to SQLite history
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from config import Config
from delivery.database import Database
from delivery.learning_engine import LearningEngine

BASE_DIR = Path(__file__).resolve().parent
CONTRACT_FILES = (
    "attendance.json",
    "risk_report.json",
    "gpa.json",
    "filtered_jobs.json",
    "housing_raw.json",
)


def load_json(path: Path) -> dict | list:
    """Read a JSON contract file; return empty structure on any failure."""
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def build_digest(cfg: Config) -> dict:
    """Build the digest payload from the current data contracts.

    Graceful empty-data handling: any missing file yields an empty section
    rather than a crash (see HANDOFF Anti-Integration-Failure Rules).
    """
    attendance_raw = load_json(cfg.data_dir / "attendance.json")
    risk_raw = load_json(cfg.data_dir / "risk_report.json")
    gpa = load_json(cfg.data_dir / "gpa.json")
    jobs = load_json(cfg.data_dir / "filtered_jobs.json")
    housing = load_json(cfg.data_dir / "housing_raw.json")

    # Merge subject names from attendance into risk_report where available
    subjects_by_code = {
        s.get("code"): s.get("name")
        for s in attendance_raw.get("subjects", []) if isinstance(s, dict)
    }
    attendance = []
    for subj in risk_raw.get("subjects", []):
        row = dict(subj)
        row.setdefault("name", subjects_by_code.get(subj.get("code"), "Unknown"))
        attendance.append(row)

    db = Database(db_path=cfg.db_path)
    return {
        "attendance": attendance,
        "jobs": jobs.get("jobs", []) if isinstance(jobs, dict) else [],
        "housing": housing.get("listings", []) if isinstance(housing, dict) else [],
        "gpa": gpa if isinstance(gpa, dict) else {},
        "weights": db.get_all_weights(),
    }


def _gather_mock(cfg: Config) -> None:
    """Populate the data dir from mock files so the pipeline runs offline."""
    for f in CONTRACT_FILES:
        src = cfg.mock_dir / f
        dst = cfg.data_dir / f
        if src.exists():
            dst.write_bytes(src.read_bytes())


def _gather_live(cfg: Config) -> bool:
    """Call the real portal/intelligence modules. Falls back to mock on failure."""
    try:
        import portal  # noqa: F401
        import intelligence  # noqa: F401
    except ImportError:
        return False
    # NOTE: real module wiring happens at Checkpoint 3 once Aaron's and
    # Sapna's branches merge. Until then, this returns False → mock fallback.
    return False


def run_pipeline(cfg: Config, mode: str = "mock") -> dict:
    if mode in ("live", "live-demo"):
        used_live = _gather_live(cfg)
        if not used_live:
            print("[orchestrator] live modules not ready — falling back to mock data")
            _gather_mock(cfg)
    else:
        _gather_mock(cfg)

    digest = build_digest(cfg)

    # Persist digest history + weights for the learning loop
    db = Database(db_path=cfg.db_path)
    db.log_digest("full", json.dumps(digest))

    result = dict(digest)
    result["status"] = "ok"
    result["mode"] = mode
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Atlas pipeline")
    parser.add_argument("--mock", action="store_true", help="use mock data (default)")
    parser.add_argument("--live", action="store_true", help="use real portal/intelligence modules")
    parser.add_argument("--live-demo", action="store_true", help="live mode with demo logging")
    args = parser.parse_args()

    cfg = Config.from_yaml()
    mode = "mock"
    if args.live or args.live_demo:
        mode = "live-demo" if args.live_demo else "live"

    result = run_pipeline(cfg, mode=mode)
    print(json.dumps({k: v for k, v in result.items() if k in ("status", "mode")}))
    print(f"[orchestrator] digest built: {len(result['jobs'])} jobs, "
          f"{len(result['housing'])} housing, {len(result['attendance'])} attendance subjects")
    print(f"[orchestrator] start the dashboard: uvicorn web.app:app --reload")


if __name__ == "__main__":
    sys.exit(main())