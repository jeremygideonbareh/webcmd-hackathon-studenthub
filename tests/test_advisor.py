"""
Unit tests for intelligence/advisor.py (AI Resume & Skills Advisor).
"""

from intelligence.advisor import analyze_resume_skills


def test_engineering_stream_analysis():
    res = analyze_resume_skills(["Python", "Git", "SQL"], stream="Engineering")
    assert res["stream"] == "Engineering"
    assert "Python" in res["matched_skills"]
    assert "Docker" in res["missing_critical_skills"]
    assert len(res["recommended_projects"]) > 0
    assert len(res["resume_bullet_suggestions"]) > 0
    assert 0 <= res["readiness_score"] <= 100


def test_psychology_stream_analysis():
    res = analyze_resume_skills(["SPSS", "Qualtrics"], stream="Psychology")
    assert res["stream"] == "Psychology"
    assert "SPSS" in res["matched_skills"]
    assert "R" in res["missing_critical_skills"]
    assert len(res["recommended_projects"]) > 0


def test_bba_stream_analysis():
    res = analyze_resume_skills(["Excel Pivot Tables", "Market Research"], stream="BBA")
    assert res["stream"] == "BBA"
    assert "Excel Pivot Tables" in res["matched_skills"]
    assert len(res["recommended_projects"]) > 0


def test_mba_stream_analysis():
    res = analyze_resume_skills(["SQL", "Tableau / PowerBI"], stream="MBA")
    assert res["stream"] == "MBA"
    assert "SQL" in res["matched_skills"]
    assert len(res["recommended_projects"]) > 0
