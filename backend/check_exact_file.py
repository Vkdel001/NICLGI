import pandas as pd
import os

file_path = r'C:\Users\Ryan EZ\OneDrive - EZ DASH LTD\Documents\letters_Motors_health\backend\uploads\health\RENEWAL_LISTING.xlsx'

print(f"Checking file: {file_path}")
print(f"File exists: {os.path.exists(file_path)}")

if os.path.exists(file_path):
    print(f"File size: {os.path.getsize(file_path)} bytes")
    
    try:
        df = pd.read_excel(file_path)
        print(f"Total rows read: {len(df)}")
        
        if 'POL_NO' in df.columns:
            valid_policies = df['POL_NO'].notna().sum()
            print(f"Valid policy numbers: {valid_policies}")
            
            # Show first 10 valid policies
            valid_df = df[df['POL_NO'].notna()]
            print("\nFirst 10 valid policy numbers:")
            for i, pol in enumerate(valid_df['POL_NO'].head(10)):
                print(f"{i+1}. {pol}")
                
            # Show last 5 valid policies
            print("\nLast 5 valid policy numbers:")
            for i, pol in enumerate(valid_df['POL_NO'].tail(5)):
                print(f"{len(valid_df)-4+i}. {pol}")
                
        else:
            print("POL_NO column not found")
            print(f"Available columns: {list(df.columns)}")
            
    except Exception as e:
        print(f"Error reading file: {e}")
else:
    print("File not found!")