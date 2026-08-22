"""Offline tests for intelligence.advisor - Groq layer + rule-based core.

No network calls: the Groq client is faked, and the no-key fallback path is
exercised by clearing GROQ_API_KEY from the environment.
"""

import types

import pytest

from intelligence.advisor import (
    BULLET_TEMPLATES,
    STREAM_SKILLS,
    _extract_bullets,
    analyze_resume_skills,
    generate_ai_bullets,
    get_groq_client,
)


def _fake_client(content):
    """Groq-client stand-in returning a canned completion."""
    completion = types.SimpleNamespace(
        choices=[types.SimpleNamespace(message=types.SimpleNamespace(content=content))]
    )
    return types.SimpleNamespace(
        chat=types.SimpleNamespace(
            completions=types.SimpleNamespace(create=lambda **kwargs: completion)
        )
    )


def _failing_client():
    def _boom(**kwargs):
        raise RuntimeError("simulated API outage")

    return types.SimpleNamespace(
        chat=types.SimpleNamespace(completions=types.SimpleNamespace(create=_boom))
    )


# --- Rule-based core ----------------------------------------------------

def test_engineering_gap_analysis():
    report = analyze_resume_skills(["Python", "Git", "SQL"], "Engineering", use_ai=False)
    assert report["matched_skills"] == ["Python", "Git", "SQL"]
    assert set(report["missing_critical_skills"]) == {"DSA", "Docker", "REST APIs"}
    assert report["readiness_score"] == 50


def test_readiness_full_and_zero():
    full = analyze_resume_skills(STREAM_SKILLS["MBA"], "MBA", use_ai=False)
    assert full["readiness_score"] == 100
    assert full["missing_critical_skills"] == []

    empty = analyze_resume_skills([], "Engineering", use_ai=False)
    assert empty["readiness_score"] == 0
    assert empty["matched_skills"] == []


def test_skill_matching_is_case_insensitive():
    report = analyze_resume_skills(["python ", "GIT"], "Engineering", use_ai=False)
    assert report["matched_skills"] == ["Python", "Git"]


def test_projects_target_missing_skills():
    report = analyze_resume_skills([], "Engineering", use_ai=False)
    titles = {project["title"] for project in report["recommended_projects"]}
    assert len(titles) == 3
    first_missing = {s for s in report["missing_critical_skills"]}
    assert first_missing & {"DSA", "Docker", "REST APIs", "SQL"}


def test_unknown_stream_raises():
    with pytest.raises(ValueError):
        analyze_resume_skills(["Python"], "Astrology")


# --- Bullet suggestions --------------------------------------------------

def test_template_fallback_without_api_key(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    report = analyze_resume_skills(["Docker", "SQL"], "Engineering")
    assert report["bullet_source"] == "template"
    assert report["resume_bullet_suggestions"] == [
        BULLET_TEMPLATES["Docker"],
        BULLET_TEMPLATES["SQL"],
    ]


def test_use_ai_false_forces_templates(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "fake-key-for-tests")
    report = analyze_resume_skills(["Docker"], "Engineering", use_ai=False)
    assert report["bullet_source"] == "template"


def test_ai_bullets_win_when_available():
    canned = (
        "- Containerized two coursework REST services with Docker and shipped them to [N] users\n"
        "- Wrote [N] SQL queries powering an analytics dashboard used by classmates\n"
        "- too short\n"
    )
    report = analyze_resume_skills(
        ["Docker", "SQL"], "Engineering", client=_fake_client(canned)
    )
    assert report["bullet_source"] == "groq"
    assert len(report["resume_bullet_suggestions"]) == 2
    assert report["resume_bullet_suggestions"][0].startswith("Containerized")


def test_ai_failure_falls_back_to_templates():
    report = analyze_resume_skills(
        ["Docker"], "Engineering", client=_failing_client()
    )
    assert report["bullet_source"] == "template"
    assert report["resume_bullet_suggestions"] == [BULLET_TEMPLATES["Docker"]]


def test_generate_ai_bullets_empty_inputs():
    assert generate_ai_bullets(None, [], [], "BBA") == []
    assert generate_ai_bullets(_fake_client("- x"), [], [], "BBA") == []


# --- LLM output parsing ---------------------------------------------------

def test_extract_bullets_handles_markdown_variants():
    raw = (
        "* Built a [N]-table SQL schema with joins and window functions\n"
        "1. Automated deployments with Docker Compose reducing setup time by [X%]\n"
        "- **Designed** CRUD REST endpoints in Flask for a campus app\n"
        "no marker but long enough sentence here to pass filter\n"
        "- short\n"
        "\"- Quoted bullet that should still parse fine\"\n"
    )
    bullets = _extract_bullets(raw)
    assert len(bullets) >= 4
    assert all("short" not in b.split() for b in bullets)
    assert bullets[2].startswith("Designed")


def test_extract_bullets_caps_at_limit():
    raw = "\n".join(f"- Bullet number {i} about skill usage" for i in range(20))
    assert len(_extract_bullets(raw)) <= 6


def test_no_key_means_no_client(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    assert get_groq_client() is None
