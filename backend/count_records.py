
import pandas as pd
import sys
import traceback

try:
    df = pd.read_excel('output_motor_renewal.xlsx')
    count = len(df)
    print(f"SUCCESS:{count}")
except Exception as e:
    print(f"ERROR:{str(e)}")
    traceback.print_exc()
