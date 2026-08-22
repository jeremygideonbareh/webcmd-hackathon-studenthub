"""
Interactive / Standalone CLI runner for the Portal Subsystem.

Usage:
    python portal/run_portal.py --mock
    python portal/run_portal.py --live
"""

import argparse
import json
import os
import sys

# Ensure UTF-8 output on Windows consoles if supported
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure parent directory is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import portal


def main():
    parser = argparse.ArgumentParser(description="Atlas Portal Subsystem Runner (Aaron)")
    parser.add_argument(
        "--mock",
        action="store_true",
        default=True,
        help="Use mock data contracts (default: True)"
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Attempt live WebCMD scrape from KP portal"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.85,
        help="Attendance threshold ratio (default: 0.85)"
    )
    args = parser.parse_args()

    use_mock = not args.live

    print("=" * 60)
    print("ATLAS PORTAL SUBSYSTEM (Role: Portal Engineer)")
    print(f"Mode: {'LIVE WEBCMD SCRAPE' if args.live else 'MOCK / CACHE DATA'}")
    print(f"Threshold: {args.threshold * 100:.1f}%")
    print("=" * 60)

    # 1. Attendance Scraping
    print("\n[1] Fetching Attendance...")
    try:
        attendance = portal.get_attendance(use_mock=use_mock)
        print(f"  Student: {attendance.get('student_name')} ({attendance.get('student_id')})")
        print(f"  Semester: {attendance.get('semester')}")
        print(f"  Subjects Scraped: {len(attendance.get('subjects', []))}")
        for subj in attendance.get("subjects", []):
            print(f"    - {subj['code']}: {subj['name']} -> {subj['classes_present']}/{subj['classes_total']} ({subj['attendance_pct']}%) [{subj['status']}]")
    except Exception as e:
        print(f"  [ERROR] Failed to fetch attendance: {e}")
        return

    # 2. Attendance Calculus & Risk Report
    print("\n[2] Generating Attendance Calculus & Risk Report...")
    try:
        risk_report = portal.get_risk_report(attendance_data=attendance, threshold=args.threshold)
        for subj in risk_report.get("subjects", []):
            badge = f"[{subj['risk_level']}]"
            print(f"\n  {badge} {subj['code']} - {subj['name']}")
            print(f"     Current: {subj['current_pct']}% ({subj['classes_present']}/{subj['classes_total']} classes)")
            if subj['classes_can_skip'] > 0:
                print(f"     Can Skip: {subj['classes_can_skip']} class(es)")
            if subj['classes_must_attend'] > 0:
                print(f"     Must Attend: {subj['classes_must_attend']} consecutive class(es)")
            print(f"     Projection: {subj['projection']}")
    except Exception as e:
        print(f"  [ERROR] Failed to calculate risk: {e}")

    # 3. GPA Extraction
    print("\n[3] Fetching GPA & Trend...")
    try:
        gpa = portal.get_gpa(use_mock=use_mock)
        print(f"  CGPA: {gpa.get('current_cgpa')}")
        print(f"  SGPA: {gpa.get('semester_gpa')}")
        print(f"  Trend: {gpa.get('gpa_trend')}")
    except Exception as e:
        print(f"  [ERROR] Failed to fetch GPA: {e}")

    print("\n" + "=" * 60)
    print("SUCCESS: Portal Subsystem Execution Completed Successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
