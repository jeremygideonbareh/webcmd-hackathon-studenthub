"""
GPA HTML Extractor for Knowledge Pro Student Portal.

Parses KP portal GPA page HTML to extract CGPA and SGPA.
"""

import re
from typing import Any, Dict
from bs4 import BeautifulSoup


def parse_gpa_html(html: str, student_id: str = "") -> Dict[str, Any]:
    """
    Parse GPA HTML from KP portal and extract CGPA/SGPA.
    
    Args:
        html: Raw HTML content from KP portal GPA page
        student_id: Student ID to include in result
        
    Returns:
        Dictionary with student_id, current_cgpa, semester_gpa, gpa_trend
    """
    soup = BeautifulSoup(html, 'html.parser')
    
    cgpa = 0.0
    sgpa = 0.0
    
    # Find table with CGPA/SGPA
    for table in soup.find_all('table'):
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all(['td', 'th'])
            cell_texts = [cell.get_text(strip=True) for cell in cells]
            
            if len(cell_texts) >= 2:
                label = cell_texts[0].lower()
                value_str = cell_texts[1]
                
                if 'cumulative' in label or 'cgpa' in label:
                    try:
                        cgpa = float(value_str)
                    except ValueError:
                        pass
                elif 'semester' in label or 'sgpa' in label:
                    try:
                        sgpa = float(value_str)
                    except ValueError:
                        pass
    
    # Determine trend
    trend = "stable"
    if sgpa > cgpa + 0.3:
        trend = "improving"
    elif sgpa < cgpa - 0.3:
        trend = "declining"
    
    return {
        "student_id": student_id,
        "current_cgpa": cgpa,
        "semester_gpa": sgpa,
        "gpa_trend": trend
    }


def compute_gpa_trend(current_cgpa: float, previous_cgpa: float = None) -> str:
    """
    Compute GPA trend based on current and previous CGPA.
    
    Args:
        current_cgpa: Current CGPA value
        previous_cgpa: Previous CGPA value (optional)
        
    Returns:
        Trend string: "improving", "declining", or "stable"
    """
    if previous_cgpa is None:
        return "stable"
    
    if current_cgpa > previous_cgpa + 0.05:
        return "improving"
    elif current_cgpa < previous_cgpa - 0.05:
        return "declining"
    return "stable"