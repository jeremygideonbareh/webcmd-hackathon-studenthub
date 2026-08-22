"""
Supabase uploader — pushes digest + weights to the hosted Postgres backend.

Used by the local pipeline (orchestrator.py --push) so the Vercel dashboard
has fresh data. stdlib only (urllib) — mirrors the serverless functions.
"""

from __future__ import annotations

import json
import os
import urllib.request
import urllib.error

from dotenv import load_dotenv

load_dotenv()  # idempotent — orchestrator/config may already have loaded it

WEIGHT_MIN, WEIGHT_MAX = 0.1, 3.0
REACTION_MULTIPLIERS = {"👍": 1.2, "👎": 0.8, "⭐": 1.5, "🚫": 0.3}


class SupabaseStore:
    """Minimal Supabase REST client for the atlas tables."""

    def __init__(self, url: str | None = None, service_key: str | None = None):
        self.url = (url or os.environ.get("SUPABASE_URL", "")).rstrip("/").strip()
        self.key = (service_key or os.environ.get("SUPABASE_SERVICE_KEY", "")).strip()

    @property
    def ready(self) -> bool:
        return bool(self.url and self.key)

    def _request(self, method: str, path: str, payload=None) -> list | dict:
        data = json.dumps(payload).encode() if payload is not None else None
        req = urllib.request.Request(
            f"{self.url}/rest/v1/{path}",
            data=data,
            method=method,
            headers={
                "apikey": self.key,
                "Authorization": f"Bearer {self.key}",
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Prefer": "return=representation",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw = resp.read().decode()
                return json.loads(raw) if raw else []
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"Supabase {e.code}: {e.read().decode()[:300]}") from e

    # --- writes ---

    def push_digest(self, digest: dict) -> None:
        """Upsert the full digest into current_digest + log to digest_history."""
        self._request(
            "POST",
            "current_digest?on_conflict=digest_type",
            {"digest_type": "full", "payload_json": digest},
        )
        self._request(
            "POST",
            "digest_history",
            {"digest_type": "full", "payload_json": digest},
        )

    def get_weights(self) -> dict[str, float]:
        rows = self._request("GET", "preference_weights?select=category,weight")
        return {r["category"]: r["weight"] for r in rows} if isinstance(rows, list) else {}

    def apply_reaction(self, item_type: str, item_id: str, reaction: str) -> dict[str, float]:
        """Log a reaction and update preference weights (learning-loop equivalent)."""
        multiplier = REACTION_MULTIPLIERS.get(reaction)
        self._request(
            "POST",
            "reactions",
            {"message_id": item_id or "feedback", "item_type": item_type, "item_id": item_id, "reaction": reaction},
        )
        if multiplier is None:
            return self.get_weights()

        digest = self._get_current_digest()
        categories = self._extract_categories(item_type, item_id, digest)
        weights = self.get_weights()
        for cat in categories:
            current = weights.get(cat, 1.0)
            new_weight = max(WEIGHT_MIN, min(WEIGHT_MAX, current * multiplier))
            self._request(
                "POST",
                "preference_weights?on_conflict=category",
                {"category": cat, "weight": new_weight},
            )
            weights[cat] = new_weight
        return weights

    def _get_current_digest(self) -> dict:
        rows = self._request("GET", "current_digest?digest_type=eq.full&select=payload_json&limit=1")
        return rows[0]["payload_json"] if rows else {}

    def _extract_categories(self, item_type: str, item_id: str, digest: dict) -> list[str]:
        for section in ("jobs", "housing"):
            for item in digest.get(section, []):
                if str(item.get("id")) == str(item_id):
                    cats = item.get("categories")
                    if cats:
                        return list(cats)
                    skills = item.get("skills_required")
                    if skills:
                        return [f"{s.lower()}_jobs" for s in skills]
        return [item_type]