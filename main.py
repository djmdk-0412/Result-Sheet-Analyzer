import os
import glob
from src.extractor import extract_subject_info_and_grades
from src.processor import process_results

# CONFIG PATHS
INPUT_DIR = 'input_pdfs'
OUTPUT_DIR = 'output'
CONFIG_FILE = os.path.join('config', 'credits.json')
DB_FILE = os.path.join('config', 'student_db.xlsx')  # <--- NEW PATH
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'Electrical_Dept_Final_GPA.xlsx')

def main():
    print("--- University Result Sheet Analyzer ---")
    
    if not os.path.exists(INPUT_DIR):
        os.makedirs(INPUT_DIR)
        return

    # Create empty db file instruction if missing
    if not os.path.exists(DB_FILE):
        print(f"NOTE: 'student_db.xlsx' not found in config/. Results will imply IDs only.")

    pdf_files = glob.glob(os.path.join(INPUT_DIR, "*.pdf"))
    
    extracted_subjects = []
    
    # 1. Extraction Phase
    for pdf_path in pdf_files:
        try:
            subject_code, df = extract_subject_info_and_grades(pdf_path)
            extracted_subjects.append((subject_code, df))
        except Exception as e:
            print(f"Error extracting {os.path.basename(pdf_path)}: {e}")

    # 2. Processing Phase
    if extracted_subjects:
        try:
            print("Merging data...")
            # We now pass DB_FILE into the function
            final_df = process_results(extracted_subjects, CONFIG_FILE, DB_FILE)
            
            final_df.to_excel(OUTPUT_FILE, index=False)
            print(f"\nSUCCESS! Results saved to: {OUTPUT_FILE}")
            print(final_df.head())
            
        except Exception as e:
            print(f"Error during processing: {e}")

if __name__ == "__main__":
    main()