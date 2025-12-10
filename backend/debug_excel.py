import pandas as pd
import os

file_path = 'uploads/health/RENEWAL_LISTING.xlsx'
print(f"Analyzing file: {file_path}")
print(f"File size: {os.path.getsize(file_path)} bytes")

df = pd.read_excel(file_path)
print(f"Total rows read by pandas: {len(df)}")
print(f"Columns: {list(df.columns)}")

if 'POL_NO' in df.columns:
    print(f"Rows with POL_NO data: {df['POL_NO'].notna().sum()}")
    print(f"Rows with empty POL_NO: {df['POL_NO'].isna().sum()}")
    
    print("\nFirst 10 POL_NO values:")
    for i, pol in enumerate(df['POL_NO'].head(10)):
        print(f"Row {i}: '{pol}'")
    
    print("\nLast 10 POL_NO values:")
    for i, pol in enumerate(df['POL_NO'].tail(10)):
        print(f"Row {len(df)-10+i}: '{pol}'")
        
    # Check for actual data rows
    non_empty_rows = df.dropna(subset=['POL_NO'])
    print(f"\nRows with actual policy numbers: {len(non_empty_rows)}")
    
    if len(non_empty_rows) > 0:
        print("Policy numbers found:")
        for pol in non_empty_rows['POL_NO'].head(10):
            print(f"  - {pol}")