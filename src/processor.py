"""
src/processor.py
Handles merging of subject grades, calculating GPA, and incorporating Student Database info.
"""
import pandas as pd
import json
import os
from src.utils import get_grade_point

def load_json(config_path):
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def calculate_gpa(row, subject_columns, credit_map):
    total_points = 0.0
    total_credits = 0.0
    
    for subject in subject_columns:
        if subject not in row or pd.isna(row[subject]):
            continue
            
        grade = str(row[subject])
        grade_point = get_grade_point(grade)
        credit = credit_map.get(subject, 0)
        
        if grade_point is not None and credit > 0:
            total_points += (grade_point * credit)
            total_credits += credit
            
    if total_credits == 0:
        return 0.0
    return round(total_points / total_credits, 2)

def attach_student_names(results_df, db_path):
    """
    Reads the Student DB (Excel/CSV) and merges names into the result sheet.
    """
    if not os.path.exists(db_path):
        print(f"WARNING: Student Database not found at {db_path}. Names will be empty.")
        return results_df

    print(f"Loading Student Database from: {db_path} ...")
    try:
        if db_path.endswith('.csv'):
            names_df = pd.read_csv(db_path)
        else:
            names_df = pd.read_excel(db_path)
            
        # Basic cleanup: Standardize Index column
        # We assume 1st column is Index, 2nd column is Name (unless headers exist)
        # Force column names for consistency if they look like default (0, 1) or 'Index No'
        
        # Clean Headers to remove spaces/lowercase
        names_df.columns = [c.strip().lower() for c in names_df.columns]
        
        # Find Index Column
        index_col = next((c for c in names_df.columns if 'index' in c or 'id' in c), None)
        name_col  = next((c for c in names_df.columns if 'name' in c), None)

        if not index_col or not name_col:
            # Fallback: Assume Col 0 is Index, Col 1 is Name
            print("   -> Header mismatch. Assuming Col 0=Index, Col 1=Name")
            index_col = names_df.columns[0]
            name_col = names_df.columns[1]

        # Standardize Data
        names_df['Index'] = names_df[index_col].astype(str).str.strip().str.replace(" ", "").str.upper()
        names_df['Name'] = names_df[name_col].astype(str).str.strip()
        
        # Filter strictly for merging
        lookup_table = names_df[['Index', 'Name']].drop_duplicates(subset=['Index'])
        
        # Perform Left Merge
        merged = pd.merge(results_df, lookup_table, on='Index', how='left')
        
        return merged

    except Exception as e:
        print(f"   -> Error reading Student Database: {e}")
        return results_df

def process_results(subject_data_list, credit_config_path, student_db_path):
    credit_map = load_json(credit_config_path)
    
    valid_dfs = []
    
    # 1. Filter out Empty DataFrames
    for subj_code, df in subject_data_list:
        if df.empty:
            print(f"!!! SKIPPING MERGE: Subject {subj_code} has no data.")
            continue
        df_renamed = df.rename(columns={'Grade': subj_code})
        valid_dfs.append(df_renamed)

    if not valid_dfs:
        raise ValueError("No valid student data found in ANY file.")

    # 2. Find Intersection
    common_indexes = set(valid_dfs[0]['Index'])
    for df in valid_dfs[1:]:
        common_indexes = common_indexes.intersection(set(df['Index']))
    
    print(f"\n--- MERGE STATS ---")
    print(f"Eligible Students (Found in all {len(valid_dfs)} PDFs): {len(common_indexes)}")
    
    # 3. Build Result Table
    final_df = pd.DataFrame(list(common_indexes), columns=['Index'])
    for df in valid_dfs:
        final_df = final_df.merge(df, on='Index', how='left')

    # 4. Attach Student Names
    final_df = attach_student_names(final_df, student_db_path)

    # 5. Calculate GPA
    valid_subjects = [c for c in final_df.columns if c not in ['Index', 'Name', 'GPA']]
    final_df['GPA'] = final_df.apply(
        lambda row: calculate_gpa(row, valid_subjects, credit_map), axis=1
    )
    
    # 6. Reorder Columns: Index | Name | [Subjects] | GPA
    cols = ['Index']
    if 'Name' in final_df.columns:
        cols.append('Name')
    
    # Sort Subject Columns Alphabetically
    cols.extend(sorted(valid_subjects))
    cols.append('GPA')
    
    final_df = final_df[cols]
    final_df.sort_values(by='Index', inplace=True)

    return final_df