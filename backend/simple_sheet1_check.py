import pandas as pd

try:
    # Read Sheet1 from RENEWAL_LISTING.xlsx in current directory
    df = pd.read_excel('RENEWAL_LISTING.xlsx', sheet_name='Sheet1')
    
    print(f"Sheet1 contains {len(df)} rows")
    
    if 'POL_NO' in df.columns:
        valid_policies = df['POL_NO'].notna().sum()
        print(f"Valid policy numbers: {valid_policies}")
        
        # Show the policies
        for i, pol in enumerate(df[df['POL_NO'].notna()]['POL_NO'], 1):
            print(f"{i}. {pol}")
    else:
        print("No POL_NO column found")
        
except Exception as e:
    print(f"Error: {e}")