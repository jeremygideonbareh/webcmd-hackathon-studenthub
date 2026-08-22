"""
Attendance HTML Extractor for Knowledge Pro Student Portal.

Parses KP portal attendance table HTML to extract structured attendance data.
"""

import re
from typing import Any, Dict, List
from bs4 import BeautifulSoup


def parse_attendance_html(html: str) -> Dict[str, Any]:
    """
    Parse attendance HTML from KP portal and extract structured data.
    
    Args:
        html: Raw HTML content from KP portal attendance page
        
    Returns:
        Dictionary with student_name, student_id, semester, and subjects list
    """
    soup = BeautifulSoup(html, 'html.parser')
    
    # Extract student info from span elements
    student_name = ""
    student_id = ""
    semester = ""
    
    # Find all spans with student info
    for span in soup.find_all('span'):
        text = span.get_text(strip=True)
        if text.startswith('Student Name'):
            student_name = text.split(':')[-1].strip()
        elif text.startswith('Register No'):
            student_id = text.split(':')[-1].strip()
        elif text.startswith('Semester'):
            semester = text.split(':')[-1].strip()
    
    # Extract attendance table
    subjects = []
    table = soup.find('table', class_='attendance-table')
    if not table:
        # Try any table
        table = soup.find('table')
    
    if table:
        rows = table.find_all('tr')
        for row in rows[1:]:  # Skip header row
            cells = row.find_all(['td', 'th'])
            cell_texts = [cell.get_text(strip=True) for cell in cells]
            
            if len(cell_texts) >= 6:
                try:
                    code = cell_texts[0]
                    name = cell_texts[1]
                    classes_held = int(re.sub(r'[^\d]', '', cell_texts[2]))
                    classes_attended = int(re.sub(r'[^\d]', '', cell_texts[3]))
                    percentage_str = cell_texts[4].replace('%', '')
                    attendance_pct = float(percentage_str)
                    status = cell_texts[5]
                    
                    # Normalize status
                    if attendance_pct >= 90:
                        status = "OK"
                    elif attendance_pct >= 85:
                        status = "OK"
                    elif attendance_pct >= 80:
                        status = "WARNING"
                    else:
                        status = "WARNING"
                    
                    subjects.append({
                        "code": code,
                        "name": name,
                        "classes_present": classes_attended,
                        "classes_total": classes_held,
                        "attendance_pct": round(attendance_pct, 2),
                        "status": status
                    })
                except (ValueError, IndexError):
                    continue
    
    return {
        "student_name": student_name,
        "student_id": student_id,
        "semester": semester,
        "subjects": subjects
    }