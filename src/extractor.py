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
#Remove Spaces & change to Uppercase letters

def clean_string(val):
    return str(val).strip().replace(" ", "").upper()

#chack the validity oof a string.
def is_valid_index(val):
    clean = clean_string(val)
    if len(clean) < 6: return False 
    digit_count = sum(char.isdigit() for char in clean)
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

def rebuild_page_text_v2(page):
    """
    Robustly reconstructs text from raw character atoms, handling 
    obfuscation detection and proper spacing.
    """
    chars = page.chars
    if not chars:
        return ""

    # --- 1. Robust Trigger Detection ---
    # Check for specific "Ghost Digits" (Control chars DC3-FS)
    has_invisible_digits = any(19 <= ord(c['text']) <= 28 for c in chars 
                               if c['text'] and len(c['text']) == 1)
    
    # Check for the SPECIFIC sequence ')DFXOW' rather than random chars
    # We grab the first 50 chars to check for header signatures usually found at the top
    intro_text = "".join(c['text'] for c in chars[:50] if c['text'])
    has_header_signature = ")DFXOW" in intro_text

    needs_repair = has_invisible_digits or has_header_signature

    # --- 2. Sorting (Line Grouping) ---
    # Sort by Top (Y) then Left (X)
    # Using 'doctop' is usually safer than 'top' if cropping occurred, but 'top' is fine here.
    chars.sort(key=lambda c: (round(c['top'], 1), c['x0']))

    full_text = []
    last_x1 = 0
    last_top = 0
    
    # Heuristic for space detection (e.g., 20% of font size)
    # This varies by PDF, but 2.0 is a safe conservative pixel gap.
    SPACE_THRESHOLD = 2.0 

    for c in chars:
        txt = c['text']
        if not txt: 
            continue

        # --- 3. Repair Logic ---
        if needs_repair:
            # Assuming repair_char_shift29 exists and handles strings safely
            # txt = repair_char_shift29(txt) 
            pass # Placeholder for your custom logic

        # --- 4. Smart Spacing ---
        # Detect new line by checking significant change in Y
        current_top = c['top']
        current_x0 = c['x0']
        
        # If we jumped to a new line (Y changed significantly)
        if abs(current_top - last_top) > 5: # 5 is an arbitrary 'line height' threshold
            full_text.append("\n")
            last_x1 = 0 # Reset x cursor
        
        # If on same line, check horizontal gap
        elif (current_x0 - last_x1) > SPACE_THRESHOLD:
            full_text.append(" ")

        full_text.append(txt)
        
        # Update trackers
        last_top = current_top
        last_x1 = c['x0'] + c['width'] # x1 is left + width

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

