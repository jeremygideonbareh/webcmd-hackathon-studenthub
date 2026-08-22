"""
Unit tests for portal/attendance_calculus.py simulate_attendance.
"""

from portal.attendance_calculus import simulate_attendance


def test_simulate_attendance_attend():
    # Present 40, Total 50 = 80%. Future attend 5 classes => 45/55 = 81.82%
    res = simulate_attendance(40, 50, future_attend=5, future_miss=0)
    assert res["current_pct"] == 81.82
    assert res["classes_present"] == 45
    assert res["classes_total"] == 55


def test_simulate_attendance_miss():
    # Present 45, Total 50 = 90%. Future miss 5 classes => 45/55 = 81.82%
    res = simulate_attendance(45, 50, future_attend=0, future_miss=5)
    assert res["current_pct"] == 81.82
    assert res["risk_level"] == "WARNING"
