import pandas as pd
import os

file_path = r'C:\Users\Ryan EZ\OneDrive - EZ DASH LTD\Documents\letters_Motors_health\backend\RENEWAL_LISTING.xlsx'

print(f"Reading Sheet1 from: {file_path}")
print(f"File exists: {os.path.exists(file_path)}")

if os.path.exists(file_path):
    try:
        # Read specifically from Sheet1
        df_sheet1 = pd.read_excel(file_path, sheet_name='Sheet1', engine='openpyxl')
        
        print(f"\n=== SHEET1 ANALYSIS ===")
        print(f"Total rows in Sheet1: {len(df_sheet1)}")
        
        if 'POL_NO' in df_sheet1.columns:
            # Count valid policy numbers (non-null)
            valid_policies = df_sheet1['POL_NO'].notna().sum()
            print(f"Valid policy numbers in Sheet1: {valid_policies}")
            
            # Show the policy numbers
            valid_df = df_sheet1[df_sheet1['POL_NO'].notna()]
            print(f"\nPolicy numbers found in Sheet1:")
            for i, pol in enumerate(valid_df['POL_NO'], 1):
                print(f"{i}. {pol}")
                
            # Show names too
            if 'NAME' in df_sheet1.columns and 'SURNAME' in df_sheet1.columns:
                print(f"\nCustomer names in Sheet1:")
                for i, (name, surname) in enumerate(zip(valid_df['NAME'], valid_df['SURNAME']), 1):
                    print(f"{i}. {name} {surname}")
        else:
            print("POL_NO column not found in Sheet1")
            print(f"Available columns in Sheet1: {list(df_sheet1.columns)}")
            
    except Exception as e:
        print(f"Error reading Sheet1: {e}")
else:
    print("File not found!")