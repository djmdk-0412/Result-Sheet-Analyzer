"""
src/utils.py
Contains global constants and mapping dictionaries for GPA calculation.
"""

# Requirement 6: Predefined grade point mapping
# IMPORTANT: All keys must be UPPERCASE to match the normalization logic below.
GRADE_POINTS = {
    'A+': 4.0, 
    'A':  4.0,
    'A-': 3.7,
    'B+': 3.3, 
    'B':  3.0, 
    'B-': 2.7,
    'C+': 2.3, 
    'C':  2.0, 
    'C-': 1.7,
    'D+': 1.3, 
    'D':  1.0,
    'E':  0.0,
    'F':  0.0,
    
    # Incomplete Grades (treated as 0.0 for calculation)
    'I':    0.0,
    'I-WE': 0.0,  # <--- This checks specifically for the PDF text
    'I-CA': 0.0,  
    'N':    0.0,
    'W':    0.0,
    
    # Valid "Exemptions" (treated as Null/None - Ignored in Calc)
    'ABS': None,  # Absent usually acts as fail (0.0) OR Exemption depending on university rule. 
                  # Change to 0.0 if Absent counts as Fail.
    'MC':  None,  # Medical Certificate (Exempt)
}

def get_grade_point(grade_str):
    """
    Standardizes grade string and returns corresponding point.
    Returns:
        float: The grade point (4.0, 3.0, 0.0)
        None:  If grade is invalid OR is an exemption (like MC)
    """
    if not isinstance(grade_str, str):
        return None
    
    # 1. Standardize (Remove spaces, convert to Upper)
    clean_grade = grade_str.strip().replace(" ", "").upper()
    
    # 2. Get value
    # If the key isn't found, it returns None (skipped)
    return GRADE_POINTS.get(clean_grade, None)