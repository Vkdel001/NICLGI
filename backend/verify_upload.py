import pandas as pd
import os

# Check the uploaded file
upload_path = 'uploads/health/RENEWAL_LISTING.xlsx'
if os.path.exists(upload_path):
    df = pd.read_excel(upload_path)
    print(f"UPLOADED FILE: {len(df)} total rows")
    if 'POL_NO' in df.columns:
        valid_policies = df['POL_NO'].notna().sum()
        print(f"UPLOADED FILE: {valid_policies} valid policy numbers")
        print("First 5 policy numbers:")
        for pol in df[df['POL_NO'].notna()]['POL_NO'].head(5):
            print(f"  - {pol}")
else:
    print("UPLOADED FILE: Not found")

# Check if there's a file in backend root
backend_path = 'RENEWAL_LISTING.xlsx'
if os.path.exists(backend_path):
    df2 = pd.read_excel(backend_path)
    print(f"\nBACKEND FILE: {len(df2)} total rows")
    if 'POL_NO' in df2.columns:
        valid_policies2 = df2['POL_NO'].notna().sum()
        print(f"BACKEND FILE: {valid_policies2} valid policy numbers")
else:
    print("\nBACKEND FILE: Not found")