"""
src/extractor.py
The 'Nuclear' Option: Rebuilds text atom-by-atom to fix 'Shift-29' 
encoding where numbers become invisible characters.
"""
import pdfplumber
import pandas as pd
import re
import os

# --- UTILS ---
def clean_string(val):
    return str(val).strip().replace(" ", "").upper()

def is_valid_index(val):
    clean = clean_string(val)
    if len(clean) < 6: return False 
    digit_count = sum(c.isdigit() for c in clean)
    return digit_count >= 4  # Allow 1 or 2 bad chars, but need mostly digits

def is_valid_grade(val):
    s = str(val).strip().upper()
    valid_starts = {'A', 'B', 'C', 'D', 'E', 'F', 'I', 'S', 'W', 'AB', 'N'}
    return s and (s[0] in valid_starts)

# --- REPAIR LOGIC ---
def repair_char_shift29(char_text):
    """
    Magic Decoder for Shift-29.
    Restores Digits (ASCII 19-28 -> 48-57) and Letters.
    """
    if not char_text: return ""
    code = ord(char_text[0]) # Get ASCII ID

    # CASE A: Invisible Digits (The reason EE2034 failed)
    # ASCII 19 (Device Control 3) -> '0' (48)
    if 19 <= code <= 28:
        return chr(code + 29)
    
    # CASE B: Shifted Letters (Common in headers)
    # Map range of printable chars back to correct letters
    if 33 <= (code + 29) <= 126:
        return chr(code + 29)

    return char_text

def rebuild_page_text(page):
    """
    Ignore extract_text()! We grab raw character atoms, sort them,
    decode them, and paste them into a long string.
    """
    # 1. Grab all characters
    chars = page.chars
    if not chars: return ""

    # 2. Check Encryption Signature
    # If we see any of the "Ghost Digits" (ASCII 19-28), we know we must repair.
    has_invisible_digits = any(19 <= ord(c['text']) <= 28 for c in chars if c['text'])
    has_header_signature = any(c['text'] == ')' for c in chars) and any(c['text'] == 'D' for c in chars) # Part of ')DFXOW'
    
    needs_repair = has_invisible_digits or has_header_signature

    # 3. Process
    # Sort characters by Y (top) then X (left) to form lines
    # Tolerance helps group letters into lines slightly unevenly formatted
    chars.sort(key=lambda c: (round(c['top'], 1), c['x0']))

    full_text = []
    last_top = 0

    for c in chars:
        txt = c['text']
        # Apply Fix if needed
        if needs_repair:
            txt = repair_char_shift29(txt)
        
        # Heuristic: Add space if distance from last char > font size / 2
        # (Simplified: just stream the text, Regex will handle spacing)
        full_text.append(txt)
        
    return "".join(full_text)

# --- MAIN FUNCTION ---
def extract_subject_info_and_grades(pdf_path):
    extracted_data = []
    subject_code = None
    
    print(f"DEBUG: Scanning {os.path.basename(pdf_path)}...")

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            # 1. Rebuild Text (The Fix)
            # This brings the numbers back from "Invisible" realm
            text = rebuild_page_text(page)
            
            # 2. Code Detection
            if not subject_code:
                # Strong Regex
                match = re.search(r"([A-Z]{2}\d{4})", text)
                if match: subject_code = match.group(1)

            # 3. Extraction (Pattern Based)
            # Since formatting is strictly "INDEX GRADE", we can just regex the stream.
            # Look for 6-7 char Index followed by Grade
            
            # Regex Explanation:
            # (?<!\d)       : Ensure not part of longer number
            # (\d{6}[A-Z])  : Capture Group 1 (Index: 6 digits + Letter) e.g. 230007J
            # .*?           : Non-greedy garbage/space match
            # ([A-C][\+\-]?|[FIEWS]|AB|ABS) : Capture Group 2 (Grade)
            
            pattern = re.compile(r"(\d{5,7}[A-Z])\s*([A-D][\+\-]?|[FIEWS][\-a-z]*|ABS|AB)")
            
            matches = pattern.findall(text)
            
            for m in matches:
                idx = m[0]
                grd = m[1]
                
                # Double clean grades like "I-we" -> "I" if needed, or keep full
                # Remove small letters if only first capital matters?
                # User config seemed to only care about first letter mostly, but "I" handled as 0.
                
                extracted_data.append({
                    'Index': clean_string(idx),
                    'Grade': grd.upper()
                })

    # Fallback Subject Code
    if not subject_code:
        fname = os.path.basename(pdf_path)
        m = re.search(r"([A-Z]{2}\d{4})", fname)
        subject_code = m.group(1) if m else ("UNKNOWN_" + fname[:5])

    df = pd.DataFrame(extracted_data)

    if df.empty:
         # One last try: Maybe Indexes look different? 
         print(f"   -> WARNING: {subject_code} - Extraction yielded 0 records.")
         return subject_code, pd.DataFrame(columns=['Index', 'Grade'])

    # Sanity: Remove dupes
    df = df.drop_duplicates(subset=['Index'], keep='last')
    print(f"   -> Detected Subject: {subject_code} ({len(df)} records | Sample: {df.iloc[0]['Index']})")

    return subject_code, df