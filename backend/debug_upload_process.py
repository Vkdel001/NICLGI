import pandas as pd
import os

# This simulates exactly what the upload route does during the Python fallback
print("=== DEBUGGING UPLOAD PROCESS ===")

# Check if RENEWAL_LISTING.xlsx exists in current directory (backend folder)
if os.path.exists('RENEWAL_LISTING.xlsx'):
    print("✅ RENEWAL_LISTING.xlsx found in backend directory")
    
    # This is exactly what the upload route Python script does
    try:
        df = pd.read_excel('RENEWAL_LISTING.xlsx')
        print(f"📊 Python reads: {len(df)} rows (this is what upload shows)")
        
        # Check all sheets
        excel_file = pd.ExcelFile('RENEWAL_LISTING.xlsx')
        print(f"📋 Available sheets: {excel_file.sheet_names}")
        
        # Check each sheet
        for sheet_name in excel_file.sheet_names:
            df_sheet = pd.read_excel('RENEWAL_LISTING.xlsx', sheet_name=sheet_name)
            print(f"   Sheet '{sheet_name}': {len(df_sheet)} rows")
            
        # Check what the default read gets
        print(f"\n🔍 Default pd.read_excel() reads from sheet: '{excel_file.sheet_names[0]}'")
        
    except Exception as e:
        print(f"❌ Error: {e}")
else:
    print("❌ RENEWAL_LISTING.xlsx NOT found in backend directory")

# Also check the uploads folder
uploads_path = 'uploads/health/RENEWAL_LISTING.xlsx'
if os.path.exists(uploads_path):
    print(f"\n=== UPLOADS FOLDER FILE ===")
    try:
        df_uploads = pd.read_excel(uploads_path)
        print(f"📊 Uploads file has: {len(df_uploads)} rows")
        
        excel_file_uploads = pd.ExcelFile(uploads_path)
        print(f"📋 Uploads file sheets: {excel_file_uploads.sheet_names}")
        
        for sheet_name in excel_file_uploads.sheet_names:
            df_sheet = pd.read_excel(uploads_path, sheet_name=sheet_name)
            print(f"   Sheet '{sheet_name}': {len(df_sheet)} rows")
            
    except Exception as e:
        print(f"❌ Uploads file error: {e}")
else:
    print("❌ No file in uploads folder")