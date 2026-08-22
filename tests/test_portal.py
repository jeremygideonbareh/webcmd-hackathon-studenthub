"""
Unit and integration tests for Portal extractor and public API facade.
Works with both pytest and python -m unittest.
"""

import unittest
import portal
from portal.attendance_extractor import parse_attendance_html
from portal.gpa_extractor import parse_gpa_html, compute_gpa_trend


SAMPLE_KP_ATTENDANCE_HTML = """
<html>
<body>
  <div>
    <span>Student Name : Rahul Kumar</span>
    <span>Register No : 22BCE1234</span>
    <span>Semester : Fall 2026</span>
  </div>
  <table class="attendance-table" border="1">
    <tr>
      <th>Subject Code</th>
      <th>Subject Name</th>
      <th>Classes Held</th>
      <th>Classes Attended</th>
      <th>Percentage</th>
      <th>Status</th>
    </tr>
    <tr>
      <td>EEE1001</td>
      <td>Basic Electrical Engineering</td>
      <td>52</td>
      <td>42</td>
      <td>80.77%</td>
      <td>Active</td>
    </tr>
    <tr>
      <td>CSE2001</td>
      <td>Data Structures & Algorithms</td>
      <td>50</td>
      <td>48</td>
      <td>96.00%</td>
      <td>Active</td>
    </tr>
  </table>
</body>
</html>
"""

SAMPLE_KP_GPA_HTML = """
<html>
<body>
  <div>
    <span>Register No: 22BCE1234</span>
    <table>
      <tr><td>Cumulative Grade Point Average (CGPA):</td><td>8.45</td></tr>
      <tr><td>Semester Grade Point Average (SGPA):</td><td>8.72</td></tr>
    </table>
  </div>
</body>
</html>
"""


class TestPortalExtractor(unittest.TestCase):
    def test_parse_attendance_html(self):
        data = parse_attendance_html(SAMPLE_KP_ATTENDANCE_HTML)
        self.assertEqual(data["student_name"], "Rahul Kumar")
        self.assertEqual(data["student_id"], "22BCE1234")
        self.assertEqual(len(data["subjects"]), 2)
        self.assertEqual(data["subjects"][0]["code"], "EEE1001")
        self.assertEqual(data["subjects"][0]["classes_present"], 42)
        self.assertEqual(data["subjects"][0]["classes_total"], 52)
        self.assertEqual(data["subjects"][0]["attendance_pct"], 80.77)
        self.assertEqual(data["subjects"][0]["status"], "WARNING")

    def test_parse_gpa_html(self):
        gpa_data = parse_gpa_html(SAMPLE_KP_GPA_HTML, student_id="22BCE1234")
        self.assertEqual(gpa_data["student_id"], "22BCE1234")
        self.assertEqual(gpa_data["current_cgpa"], 8.45)
        self.assertEqual(gpa_data["semester_gpa"], 8.72)
        self.assertEqual(gpa_data["gpa_trend"], "stable")

    def test_portal_public_facade(self):
        """Verify that portal public functions return valid mock data when use_mock=True."""
        attendance = portal.get_attendance(use_mock=True)
        self.assertEqual(attendance["student_name"], "Rahul Kumar")
        self.assertTrue(len(attendance["subjects"]) >= 1)

        risk = portal.get_risk_report(attendance_data=attendance, threshold=0.85)
        self.assertEqual(risk["threshold_pct"], 85.0)
        self.assertEqual(len(risk["subjects"]), len(attendance["subjects"]))

        gpa = portal.get_gpa(use_mock=True)
        self.assertEqual(gpa["student_id"], "22BCE1234")
        self.assertEqual(gpa["current_cgpa"], 8.45)


if __name__ == "__main__":
    unittest.main()
