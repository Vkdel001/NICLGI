import pandas as pd
import os

backend_file = r'C:\Users\Ryan EZ\OneDrive - EZ DASH LTD\Documents\letters_Motors_health\backend\RENEWAL_LISTING.xlsx'

print(f"Checking backend file: {backend_file}")
print(f"File exists: {os.path.exists(backend_file)}")

if os.path.exists(backend_file):
    print(f"File size: {os.path.getsize(backend_file)} bytes")
    
    try:
        df = pd.read_excel(backend_file)
        print(f"Total rows read: {len(df)}")
        
        if 'POL_NO' in df.columns:
            valid_policies = df['POL_NO'].notna().sum()
            print(f"Valid policy numbers: {valid_policies}")
            
            # Show first 10 valid policies
            valid_df = df[df['POL_NO'].notna()]
            print("\nFirst 10 valid policy numbers:")
            for i, pol in enumerate(valid_df['POL_NO'].head(10)):
                print(f"{i+1}. {pol}")
                
        else:
            print("POL_NO column not found")
            print(f"Available columns: {list(df.columns)}")
            
    except Exception as e:
        print(f"Error reading file: {e}")
else:
    print("Backend file not found!")

# Also check the uploads file again
uploads_file = r'C:\Users\Ryan EZ\OneDrive - EZ DASH LTD\Documents\letters_Motors_health\backend\uploads\health\RENEWAL_LISTING.xlsx'
print(f"\n--- UPLOADS FILE ---")
print(f"Checking uploads file: {uploads_file}")
print(f"File exists: {os.path.exists(uploads_file)}")

if os.path.exists(uploads_file):
    print(f"File size: {os.path.getsize(uploads_file)} bytes")
    
    try:
        df2 = pd.read_excel(uploads_file)
        print(f"Total rows read: {len(df2)}")
        
        if 'POL_NO' in df2.columns:
            valid_policies2 = df2['POL_NO'].notna().sum()
            print(f"Valid policy numbers: {valid_policies2}")
            
        else:
            print("POL_NO column not found")
            
    except Exception as e:
        print(f"Error reading uploads file: {e}")

# Check modification times
print(f"\n--- FILE TIMESTAMPS ---")
if os.path.exists(backend_file):
    backend_mtime = os.path.getmtime(backend_file)
    print(f"Backend file modified: {backend_mtime}")
    
if os.path.exists(uploads_file):
    uploads_mtime = os.path.getmtime(uploads_file)
    print(f"Uploads file modified: {uploads_mtime}")
    
    if os.path.exists(backend_file):
        if backend_mtime > uploads_mtime:
            print("⚠️ Backend file is NEWER than uploads file!")
        elif uploads_mtime > backend_mtime:
            print("✅ Uploads file is newer than backend file")
        else:
            print("📅 Both files have same timestamp")