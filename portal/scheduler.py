"""
Daily Attendance Scheduler for Atlas Portal Subsystem.

Schedules automatic attendance checks and alerts:
- Morning Check: 08:55 AM (before morning lectures)
- Evening Check: 04:05 PM (after afternoon lectures)

Supports:
1. Python in-process background loop
2. Windows Task Scheduler registration for persistent background execution
"""

import argparse
import os
import subprocess
import sys
import time
from datetime import datetime

# Ensure UTF-8 output encoding
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure parent directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from portal.notifier import send_attendance_notification


def run_scheduler_loop():
    """Run persistent loop checking time and triggering at 08:55 and 16:05."""
    print("=" * 60)
    print("ATLAS ATTENDANCE SCHEDULER ACTIVE")
    print("Target Schedule: 08:55 AM & 04:05 PM daily")
    print("=" * 60)

    last_triggered_date_slot = None

    while True:
        now = datetime.now()
        current_time_str = now.strftime("%H:%M")
        current_date_str = now.strftime("%Y-%m-%d")

        # 08:55 AM slot
        if current_time_str == "08:55" and last_triggered_date_slot != f"{current_date_str}_morning":
            print(f"\n[Scheduler] Morning slot reached (08:55 AM). Running attendance check...")
            send_attendance_notification()
            last_triggered_date_slot = f"{current_date_str}_morning"

        # 04:05 PM slot (16:05)
        elif current_time_str == "16:05" and last_triggered_date_slot != f"{current_date_str}_evening":
            print(f"\n[Scheduler] Evening slot reached (04:05 PM). Running attendance check...")
            send_attendance_notification()
            last_triggered_date_slot = f"{current_date_str}_evening"

        time.sleep(20)


def setup_windows_scheduled_tasks():
    """Register persistent Windows Scheduled Tasks for 08:55 AM and 04:05 PM."""
    if sys.platform != "win32":
        print("Windows Task Scheduler registration is only supported on Windows.")
        return

    python_exe = sys.executable
    notifier_script = os.path.join(os.path.dirname(__file__), "notifier.py")

    cmd_morning = [
        "schtasks", "/Create", "/F",
        "/TN", "AtlasAttendance_Morning",
        "/TR", f'"{python_exe}" "{notifier_script}"',
        "/SC", "DAILY",
        "/ST", "08:55"
    ]

    cmd_evening = [
        "schtasks", "/Create", "/F",
        "/TN", "AtlasAttendance_Evening",
        "/TR", f'"{python_exe}" "{notifier_script}"',
        "/SC", "DAILY",
        "/ST", "16:05"
    ]

    print("Registering Windows Scheduled Tasks...")
    res_m = subprocess.run(cmd_morning, capture_output=True, text=True)
    res_e = subprocess.run(cmd_evening, capture_output=True, text=True)

    if res_m.returncode == 0 and res_e.returncode == 0:
        print("SUCCESS: Both morning (08:55 AM) and evening (04:05 PM) tasks registered in Windows Task Scheduler!")
    else:
        print(f"Morning output: {res_m.stdout or res_m.stderr}")
        print(f"Evening output: {res_e.stdout or res_e.stderr}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Atlas Attendance Scheduler")
    parser.add_argument("--register-windows", action="store_true", help="Register Windows Scheduled Tasks")
    parser.add_argument("--now", action="store_true", help="Trigger notification immediately")
    args = parser.parse_args()

    if args.register_windows:
        setup_windows_scheduled_tasks()
    elif args.now:
        send_attendance_notification()
    else:
        run_scheduler_loop()
