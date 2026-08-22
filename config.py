"""
Atlas config loader — loads .env secrets + config.yaml settings into a Config dataclass.

Usage:
    from config import Config
    cfg = Config()
    cfg.attendance_threshold  # 0.85
    cfg.kp_username           # from .env
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


@dataclass
class Config:
    """Central application configuration."""

    # Paths
    base_dir: Path = BASE_DIR
    data_dir: Path = field(default_factory=lambda: BASE_DIR / "data")
    mock_dir: Path = field(default_factory=lambda: BASE_DIR / "data" / "mock")
    db_path: Path = field(default_factory=lambda: BASE_DIR / "atlas.db")

    # Attendance
    attendance_threshold: float = 0.85
    risk_safe: float = 90.0
    risk_caution: float = 85.0
    risk_warning: float = 80.0

    # GPA modes
    gpa_competitive: float = 8.5
    gpa_balanced: float = 8.0

    # KP portal
    kp_portal_url: str = "https://kp.christuniversity.in/KnowledgePro"
    webcmd_profile: str = "kp_student"
    webcmd_session_id: str = ""

    # Housing
    housing_city: str = "bangalore"
    housing_locality: str = "Katpadi"
    housing_max_budget: int = 25000

    # Discord optional bonus
    discord_webhook_url: str = ""

    @classmethod
    def from_yaml(cls, path: Path | None = None) -> "Config":
        cfg = cls()
        yaml_path = path or (BASE_DIR / "config.yaml")
        if yaml_path.exists():
            raw = yaml.safe_load(yaml_path.read_text()) or {}
            for key, value in raw.items():
                if hasattr(cfg, key):
                    setattr(cfg, key, value)

        # .env overrides YAML for secrets/runtime-specific values
        env = os.environ
        if env.get("KP_PORTAL_URL"):
            cfg.kp_portal_url = env["KP_PORTAL_URL"]
        if env.get("WEBCMD_PROFILE"):
            cfg.webcmd_profile = env["WEBCMD_PROFILE"]
        if env.get("WEBCMD_SESSION_ID"):
            cfg.webcmd_session_id = env["WEBCMD_SESSION_ID"]
        if env.get("HOUSING_CITY"):
            cfg.housing_city = env["HOUSING_CITY"]
        if env.get("HOUSING_LOCALITY"):
            cfg.housing_locality = env["HOUSING_LOCALITY"]
        if env.get("HOUSING_MAX_BUDGET"):
            cfg.housing_max_budget = int(env["HOUSING_MAX_BUDGET"])
        if env.get("DISCORD_WEBHOOK_URL"):
            cfg.discord_webhook_url = env["DISCORD_WEBHOOK_URL"]
        return cfg

    # Credential accessors (raise clear errors if missing)
    @property
    def kp_username(self) -> str:
        return os.environ.get("KP_USERNAME", "")

    @property
    def kp_password(self) -> str:
        return os.environ.get("KP_PASSWORD", "")