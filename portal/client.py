"""
KP Portal Client - HTTP request handler for Knowledge Pro student portal authentication.

Handles Level 2 authentication (Register No & KP Password) for Christ University KP portal.
"""

import os
import requests
from typing import Any, Dict, Optional
from bs4 import BeautifulSoup


class KPPortalClient:
    """HTTP client for KP portal authentication and data retrieval."""
    
    BASE_URL = "https://kp.christuniversity.in/KnowledgePro"
    LOGIN_URL = f"{BASE_URL}/StudentLogin.do?method=loginStudent"
    ATTENDANCE_URL = f"{BASE_URL}/StudentLogin.do?method=initStudentWiseAttendanceSummary"
    GPA_URL = f"{BASE_URL}/StudentLogin.do?method=initStudentWiseGradeSummary"
    LOGOUT_URL = f"{BASE_URL}/StudentLogin.do?method=logout"
    
    def __init__(self, username: str = "", password: str = ""):
        self.username = username or os.getenv("KP_USERNAME", "")
        self.password = password or os.getenv("KP_PASSWORD", "")
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/x-www-form-urlencoded",
        })
        self._authenticated = False
    
    def login(self) -> bool:
        """
        Perform Level 2 authentication with Register No and KP Password.
        
        Returns:
            True if login successful, False otherwise
        """
        if not self.username or not self.password:
            raise ValueError("Username and password required for KP portal login")
        
        # Get login page first to handle any CSRF tokens or session cookies
        login_page_url = f"{self.BASE_URL}/StudentLogin.do"
        try:
            response = self.session.get(login_page_url, timeout=30)
            response.raise_for_status()
        except requests.RequestException as e:
            raise ConnectionError(f"Failed to access KP login page: {e}")
        
        # Parse for any hidden form fields
        soup = BeautifulSoup(response.text, 'html.parser')
        form_data = {
            "userName": self.username,
            "password": self.password,
        }
        
        # Add any hidden inputs
        for hidden in soup.find_all('input', type='hidden'):
            name = hidden.get('name')
            value = hidden.get('value', '')
            if name:
                form_data[name] = value
        
        # Submit login
        try:
            login_response = self.session.post(
                self.LOGIN_URL,
                data=form_data,
                allow_redirects=True,
                timeout=30
            )
            login_response.raise_for_status()
        except requests.RequestException as e:
            raise ConnectionError(f"KP portal login request failed: {e}")
        
        # Check if login was successful (look for redirect to dashboard or attendance page)
        if "StudentLogin.do" in login_response.url and "method=loginStudent" not in login_response.url:
            # Still on login page - login failed
            self._authenticated = False
            return False
        
        # Check for error messages in response
        if "invalid" in login_response.text.lower() or "error" in login_response.text.lower():
            self._authenticated = False
            return False
        
        self._authenticated = True
        return True
    
    def get_attendance_page(self) -> str:
        """
        Fetch the attendance summary page HTML.
        
        Returns:
            HTML content of attendance page
        """
        if not self._authenticated:
            if not self.login():
                raise PermissionError("Not authenticated. Login required.")
        
        try:
            response = self.session.get(self.ATTENDANCE_URL, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            raise ConnectionError(f"Failed to fetch attendance page: {e}")
    
    def get_gpa_page(self) -> str:
        """
        Fetch the GPA/grades summary page HTML.
        
        Returns:
            HTML content of GPA page
        """
        if not self._authenticated:
            if not self.login():
                raise PermissionError("Not authenticated. Login required.")
        
        try:
            response = self.session.get(self.GPA_URL, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            raise ConnectionError(f"Failed to fetch GPA page: {e}")
    
    def logout(self) -> bool:
        """
        Logout from KP portal to avoid 15-minute session lockout.
        
        Returns:
            True if logout successful
        """
        if not self._authenticated:
            return True
        
        try:
            self.session.get(self.LOGOUT_URL, timeout=10)
        except requests.RequestException:
            pass
        
        self._authenticated = False
        return True
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logout()
        self.session.close()


def login_kp_portal(username: str, password: str) -> KPPortalClient:
    """
    Convenience function to create client and login.
    
    Args:
        username: Register number
        password: KP password
        
    Returns:
        Authenticated KPPortalClient instance
    """
    client = KPPortalClient(username, password)
    if client.login():
        return client
    else:
        client.logout()
        raise PermissionError("KP portal login failed - invalid credentials")