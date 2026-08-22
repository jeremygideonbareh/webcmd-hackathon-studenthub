"""
Unit tests for Attendance Calculus Engine.
Works with both pytest and python -m unittest.
"""

import unittest
from portal.attendance_calculus import (
    calculate_subject_risk,
    generate_risk_report,
)


class TestAttendanceCalculus(unittest.TestCase):
    def test_safe_attendance_can_skip(self):
        """Student with 48/50 classes (96%) at 85% threshold can skip 6 classes."""
        res = calculate_subject_risk(present=48, total=50, threshold=0.85)
        self.assertEqual(res["current_pct"], 96.0)
        self.assertEqual(res["risk_level"], "SAFE")
        self.assertEqual(res["classes_can_skip"], 6)
        self.assertEqual(res["classes_must_attend"], 0)

    def test_warning_attendance_must_attend(self):
        """Student with 42/52 classes (80.77%) at 85% threshold must attend 15 consecutive classes."""
        res = calculate_subject_risk(present=42, total=52, threshold=0.85)
        self.assertEqual(res["current_pct"], 80.77)
        self.assertEqual(res["risk_level"], "WARNING")
        self.assertEqual(res["classes_can_skip"], 0)
        self.assertEqual(res["classes_must_attend"], 15)

    def test_danger_attendance(self):
        """Student with 30/40 classes (75.0%) at 85% threshold is in DANGER."""
        res = calculate_subject_risk(present=30, total=40, threshold=0.85)
        self.assertEqual(res["current_pct"], 75.0)
        self.assertEqual(res["risk_level"], "DANGER")
        self.assertEqual(res["classes_can_skip"], 0)
        self.assertEqual(res["classes_must_attend"], 27)

    def test_caution_attendance(self):
        """Student with 38/44 classes (86.36%) at 85% threshold is in CAUTION."""
        res = calculate_subject_risk(present=38, total=44, threshold=0.85)
        self.assertEqual(res["current_pct"], 86.36)
        self.assertEqual(res["risk_level"], "CAUTION")
        self.assertEqual(res["classes_can_skip"], 0)
        self.assertEqual(res["classes_must_attend"], 0)

    def test_zero_classes_held(self):
        """Zero classes held should return safe baseline."""
        res = calculate_subject_risk(present=0, total=0, threshold=0.85)
        self.assertEqual(res["current_pct"], 100.0)
        self.assertEqual(res["risk_level"], "SAFE")
        self.assertEqual(res["classes_can_skip"], 0)
        self.assertEqual(res["classes_must_attend"], 0)

    def test_perfect_attendance(self):
        """10/10 classes attended (100%)."""
        res = calculate_subject_risk(present=10, total=10, threshold=0.85)
        self.assertEqual(res["current_pct"], 100.0)
        self.assertEqual(res["risk_level"], "SAFE")
        self.assertEqual(res["classes_can_skip"], 1)
        self.assertEqual(res["classes_must_attend"], 0)

    def test_generate_risk_report(self):
        """Test full risk report schema contract generation."""
        attendance_mock = {
            "student_name": "Test Student",
            "student_id": "TEST1234",
            "semester": "Fall 2026",
            "subjects": [
                {
                    "code": "EEE1001",
                    "name": "Electrical Engineering",
                    "classes_present": 42,
                    "classes_total": 52,
                    "attendance_pct": 80.77,
                    "status": "WARNING"
                },
                {
                    "code": "CSE2001",
                    "name": "Data Structures",
                    "classes_present": 48,
                    "classes_total": 50,
                    "attendance_pct": 96.0,
                    "status": "OK"
                }
            ]
        }

        report = generate_risk_report(attendance_mock, threshold=0.85)
        self.assertEqual(report["threshold_pct"], 85.0)
        self.assertEqual(report["student_id"], "TEST1234")
        self.assertEqual(len(report["subjects"]), 2)
        self.assertEqual(report["subjects"][0]["code"], "EEE1001")
        self.assertEqual(report["subjects"][0]["risk_level"], "WARNING")
        self.assertEqual(report["subjects"][1]["code"], "CSE2001")
        self.assertEqual(report["subjects"][1]["risk_level"], "SAFE")


if __name__ == "__main__":
    unittest.main()
