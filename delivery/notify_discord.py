"""
Optional Discord webhook bonus — fires a one-line notification if
DISCORD_WEBHOOK_URL is set in .env. No-op otherwise.

Usage:
    from delivery.notify_discord import notify
    notify("🎯 4 new internships matched for you — check the dashboard")
"""

from __future__ import annotations

import os

import requests


def notify(message: str, webhook_url: str | None = None) -> bool:
    url = webhook_url or os.environ.get("DISCORD_WEBHOOK_URL", "")
    if not url:
        return False  # disabled — no-op
    try:
        r = requests.post(url, json={"content": message}, timeout=10)
        return r.status_code == 204 or r.status_code == 200
    except requests.RequestException:
        return False