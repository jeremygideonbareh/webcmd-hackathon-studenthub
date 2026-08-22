"""
WebCMD Python Wrapper for Atlas Portal Subsystem.

Executes deterministic JavaScript adapters using the WebCMD CLI (@agentrhq/webcmd).
Provides:
- Dynamic WebCMD session lifecycle management
- Subprocess error handling and sanitization
- Exponential backoff with randomized jitter
- Automatic response caching and offline recovery
- Data schema transformation to shared contracts
"""

import json
import os
import random
import re
import shutil
import subprocess
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from portal.attendance_extractor import parse_attendance_html
from portal.gpa_extractor import compute_gpa_trend


class WebCMDAdapter:
    """Wrapper around WebCMD CLI and KP portal scraper."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.profile = self.config.get("webcmd_profile", "kp_student")
        self.kp_base_url = self.config.get(
            "kp_base_url",
            os.getenv("KP_BASE_URL", "https://kp.christuniversity.in/KnowledgePro")
        )
        self.username = self.config.get("kp_username", os.getenv("KP_USERNAME", ""))
        self.password = self.config.get("kp_password", os.getenv("KP_PASSWORD", ""))
        
        self.adapter_dir = os.path.join(os.path.dirname(__file__), "adapters")
        self.data_dir = self.config.get(
            "data_dir",
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        )
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(os.path.join(self.data_dir, "mock"), exist_ok=True)

    def _get_env_vars(self) -> Dict[str, str]:
        """Prepare sanitized environment variables for WebCMD subprocess."""
        env = os.environ.copy()
        env["KP_BASE_URL"] = self.kp_base_url
        if self.username:
            env["KP_USERNAME"] = self.username
        if self.password:
            env["KP_PASSWORD"] = self.password
        return env

    def is_webcmd_available(self) -> bool:
        """Check if webcmd CLI is installed and discoverable on PATH."""
        return shutil.which("webcmd") is not None

    def _ensure_session(self) -> Optional[str]:
        """Ensure an active WebCMD browser session exists and return its session ID."""
        try:
            list_res = subprocess.run(
                ["webcmd", "--profile", self.profile, "session", "list"],
                capture_output=True, text=True, timeout=10
            )
            if list_res.returncode == 0:
                match = re.search(r"(session_[a-zA-Z0-9\-]+)", list_res.stdout)
                if match:
                    return match.group(1)
        except Exception:
            pass

        try:
            create_res = subprocess.run(
                ["webcmd", "--profile", self.profile, "session", "create"],
                capture_output=True, text=True, timeout=15
            )
            match = re.search(r"(session_[a-zA-Z0-9\-]+)", create_res.stdout)
            if match:
                return match.group(1)
        except Exception:
            pass

        return None

    def _run_adapter(self, adapter_filename: str, retries: int = 2) -> Dict[str, Any]:
        """
        Execute a WebCMD JavaScript adapter script via CLI with retry & jitter.
        """
        if not self.is_webcmd_available():
            raise FileNotFoundError(
                "WebCMD CLI not found on PATH. Install with: npm install -g @agentrhq/webcmd"
            )

        adapter_path = os.path.join(self.adapter_dir, adapter_filename)
        if not os.path.exists(adapter_path):
            raise FileNotFoundError(f"Adapter file not found at: {adapter_path}")

        session_id = self._ensure_session()
        cmd = ["webcmd", "--profile", self.profile]
        if session_id:
            cmd.extend(["--session", session_id])
        cmd.extend(["browser", "run", "--file", adapter_path])

        last_error = None
        for attempt in range(1, retries + 2):
            try:
                if attempt > 1:
                    jitter = random.uniform(1.0, 3.0)
                    time.sleep(jitter)

                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=90,
                    env=self._get_env_vars()
                )

                if result.returncode != 0:
                    raise RuntimeError(f"WebCMD exited with code {result.returncode}: {result.stderr or result.stdout}")

                stdout_clean = result.stdout.strip()
                json_start = stdout_clean.find("{")
                json_end = stdout_clean.rfind("}")
                if json_start != -1 and json_end != -1:
                    json_str = stdout_clean[json_start:json_end + 1]
                    data = json.loads(json_str)
                    if data.get("error"):
                        raise RuntimeError(f"Adapter execution error: {data['error']}")
                    return data
                else:
                    raise json.JSONDecodeError("No JSON structure found in output", stdout_clean, 0)

            except Exception as e:
                last_error = e
                print(f"[WebCMDAdapter] Attempt {attempt}/{retries + 1} failed: {e}")

        raise RuntimeError(f"WebCMD adapter '{adapter_filename}' failed after {retries + 1} attempts: {last_error}")

    def scrape_attendance(self, use_mock_fallback: bool = True) -> Dict[str, Any]:
        """
        Scrape attendance from KP Portal.
        Returns dictionary strictly adhering to attendance.json contract.
        """
        cache_path = os.path.join(self.data_dir, "attendance.json")

        try:
            raw = self._run_adapter("kp_attendance_adapter.js")
            
            attendance_payload = {
                "student_name": raw.get("studentName", "Student"),
                "student_id": raw.get("studentId", self.username or "22BCE1234"),
                "semester": raw.get("semester", "Fall 2026"),
                "scraped_at": raw.get("timestamp", datetime.now(timezone.utc).astimezone().isoformat()),
                "subjects": [
                    {
                        "code": item.get("subjectCode", "UNKNOWN"),
                        "name": item.get("subjectName", "Subject"),
                        "classes_present": int(item.get("classesAttended", 0)),
                        "classes_total": int(item.get("classesHeld", 0)),
                        "attendance_pct": float(item.get("percentage", 0.0)),
                        "status": "WARNING" if float(item.get("percentage", 0.0)) < 85.0 else "OK"
                    }
                    for item in raw.get("attendance", [])
                ]
            }

            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(attendance_payload, f, indent=2)

            return attendance_payload

        except Exception as e:
            print(f"[WebCMDAdapter] Attendance scrape encountered error: {e}")
            if use_mock_fallback:
                if os.path.exists(cache_path):
                    print(f"[WebCMDAdapter] Serving cached attendance data from {cache_path}")
                    with open(cache_path, "r", encoding="utf-8") as f:
                        cached = json.load(f)
                        cached["staleness_warning"] = f"Using cached data. Live scrape failed: {str(e)}"
                        return cached
                
                mock_path = os.path.join(self.data_dir, "mock", "attendance.json")
                if os.path.exists(mock_path):
                    print(f"[WebCMDAdapter] Serving mock attendance data from {mock_path}")
                    with open(mock_path, "r", encoding="utf-8") as f:
                        return json.load(f)

            raise

    def scrape_gpa(self, use_mock_fallback: bool = True) -> Dict[str, Any]:
        """
        Scrape GPA from KP Portal.
        Returns dictionary strictly adhering to gpa.json contract.
        """
        cache_path = os.path.join(self.data_dir, "gpa.json")

        try:
            raw = self._run_adapter("kp_gpa_adapter.js")
            cgpa = float(raw.get("cgpa", 0.0))
            sgpa = float(raw.get("sgpa", 0.0))
            student_id = raw.get("studentId", self.username or "22BCE1234")

            trend = compute_gpa_trend(cgpa, cache_path)

            gpa_payload = {
                "student_id": student_id,
                "current_cgpa": cgpa,
                "semester_gpa": sgpa if sgpa > 0 else cgpa,
                "scraped_at": raw.get("timestamp", datetime.now(timezone.utc).astimezone().isoformat()),
                "gpa_trend": trend
            }

            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(gpa_payload, f, indent=2)

            return gpa_payload

        except Exception as e:
            print(f"[WebCMDAdapter] GPA scrape encountered error: {e}")
            if use_mock_fallback:
                if os.path.exists(cache_path):
                    print(f"[WebCMDAdapter] Serving cached GPA data from {cache_path}")
                    with open(cache_path, "r", encoding="utf-8") as f:
                        return json.load(f)

                mock_path = os.path.join(self.data_dir, "mock", "gpa.json")
                if os.path.exists(mock_path):
                    print(f"[WebCMDAdapter] Serving mock GPA data from {mock_path}")
                    with open(mock_path, "r", encoding="utf-8") as f:
                        return json.load(f)

            raise
