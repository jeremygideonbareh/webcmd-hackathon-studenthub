"""
Attendance Notification Engine for Atlas Portal.

Sends rich notifications regarding current attendance percentage and risk projections:
1. Windows Desktop Toast Alert
2. Discord Webhook Embed (if DISCORD_WEBHOOK_URL is configured in .env)
3. Formatted Terminal Digest
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from typing import Any, Dict, Optional

# Ensure UTF-8 output encoding
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure parent directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import portal
from portal.webcmd_adapter import _load_env_file

_load_env_file()


def send_attendance_notification(use_mock: bool = False) -> Dict[str, Any]:
    """
    Fetch attendance, calculate calculus risk, and trigger desktop + Discord notifications.
    """
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"\n[{now_str}] Triggering Attendance Notification...")
    
    # 1. Fetch attendance & risk report
    attendance = portal.get_attendance(use_mock=use_mock)
    risk_report = portal.get_risk_report(attendance_data=attendance, threshold=0.85)

    subjects = risk_report.get("subjects", [])
    student_name = risk_report.get("student_name", "Student")
    student_id = risk_report.get("student_id", "2560403")

    # 2. Build summary text
    critical_subjs = [s for s in subjects if s.get("risk_level") in ["DANGER", "WARNING"]]

    title = f"Atlas Attendance Alert ({student_id})"
    
    if critical_subjs:
        top_critical = critical_subjs[0]
        body = f"Warning: {top_critical['code']} at {top_critical['current_pct']}%. Must attend next {top_critical['classes_must_attend']} classes!"
    elif subjects:
        top_subj = subjects[0]
        body = f"All clear! {top_subj['code']} at {top_subj['current_pct']}%. {top_subj['projection']}"
    else:
        body = "Attendance check completed. Current status safe."

    # 3. Send Windows Native Desktop Notification
    _send_windows_toast(title, body)

    # 4. Send Discord Webhook Notification if configured
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if webhook_url and "discord.com" in webhook_url:
        _send_discord_webhook(webhook_url, risk_report)

    print(f"  [Notification Sent] {title}: {body}")
    return risk_report


def _send_windows_toast(title: str, message: str):
    """Trigger a native Windows notification balloon/toast via PowerShell."""
    if sys.platform != "win32":
        return

    ps_script = f"""
    [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
    [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null
    $template = @"
    <toast>
        <visual>
            <binding template="ToastGeneric">
                <text>{title}</text>
                <text>{message}</text>
            </binding>
        </visual>
    </toast>
"@
    $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
    $xml.LoadXml($template)
    $toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
    [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("Atlas StudentHub").Show($toast)
    """
    try:
        subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], capture_output=True, timeout=5)
    except Exception:
        pass


def _send_discord_webhook(webhook_url: str, risk_report: Dict[str, Any]):
    """Send Discord rich embed if webhook is available."""
    try:
        import requests
        fields = []
        for s in risk_report.get("subjects", [])[:5]:
            icon = "[DANGER]" if s['risk_level'] == "DANGER" else "[WARNING]" if s['risk_level'] == "WARNING" else "[CAUTION]" if s['risk_level'] == "CAUTION" else "[SAFE]"
            fields.append({
                "name": f"{icon} {s['code']} - {s['name']} ({s['current_pct']}%)",
                "value": s['projection'],
                "inline": False
            })

        payload = {
            "username": "Atlas Attendance Bot",
            "content": f"Daily Attendance Status ({datetime.now().strftime('%I:%M %p')})",
            "embeds": [{
                "title": f"Student: {risk_report.get('student_name', 'Student')} ({risk_report.get('student_id')})",
                "description": f"Threshold Target: **{risk_report.get('threshold_pct', 85.0)}%**",
                "color": 0xe74c3c if any(s['risk_level'] == 'DANGER' for s in risk_report.get('subjects', [])) else 0x2ecc71,
                "fields": fields
            }]
        }
        requests.post(webhook_url, json=payload, timeout=10)
    except Exception as e:
        print(f"  [Discord Webhook Warning] Could not deliver to Discord: {e}")


if __name__ == "__main__":
    send_attendance_notification()
