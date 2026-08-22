"""
Self-Learning Engine — feedback reaction → preference weight updates.

Reaction mapping:
  👍 = "I like this"      → boost category weight by 1.2x
  👎 = "Not relevant"     → reduce category weight by 0.8x
  ⭐ = "Save/favorite"    → boost by 1.5x
  🚫 = "Never show this"  → reduce by 0.3x

Weights are clamped to [0.1, 3.0] to prevent runaway amplification.
Fed back into Sapna's TF-IDF matcher on the next pipeline run.

Usage:
    from delivery.database import Database
    from delivery.learning_engine import LearningEngine
    engine = LearningEngine(Database())
    engine.process_reaction("item_1", "job", "internshala_12345", "👍")
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from delivery.database import Database

# Discord emoji ↔ button label mapping (shared by UI and engine)
LIKE, DISLIKE, SAVE, BLOCK = "👍", "👎", "⭐", "🚫"

REACTION_MULTIPLIERS: dict[str, float] = {
    LIKE: 1.2,
    DISLIKE: 0.8,
    SAVE: 1.5,
    BLOCK: 0.3,
}

WEIGHT_MIN = 0.1
WEIGHT_MAX = 3.0


class LearningEngine:
    """Maps reactions to clamped preference-weight updates in SQLite."""

    def __init__(self, db: "Database"):
        self.db = db

    def process_reaction(self, message_id: str, item_type: str, item_id: str, reaction: str) -> None:
        self.db.log_reaction(message_id, item_type, item_id, reaction)
        multiplier = REACTION_MULTIPLIERS.get(reaction)
        if multiplier is None:
            return
        for category in self._extract_categories(item_type, item_id):
            current = self.db.get_weight(category)
            new_weight = max(WEIGHT_MIN, min(WEIGHT_MAX, current * multiplier))
            self.db.update_weight(category, new_weight)

    def _extract_categories(self, item_type: str, item_id: str) -> list[str]:
        """Derive preference categories from item metadata (skills/source) or fall back to item_type."""
        item = self.db.get_digest_item(item_id)
        if item:
            cats = item.get("categories")
            if cats:
                return list(cats)
            skills = item.get("skills_required")
            if skills:
                return [f"{skill.lower()}_jobs" for skill in skills]
        return [item_type]

    def get_all_weights(self) -> dict[str, float]:
        return self.db.get_all_weights()