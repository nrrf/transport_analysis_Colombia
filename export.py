import glob
import pandas as pd 
import os

pwd = os.getcwd()
print(pwd)

included_extensions = ['csv']
filenames = [fn for fn in os.listdir(pwd+'/assets')
              if any(fn.endswith(ext) for ext in included_extensions)] 

writer = pd.ExcelWriter('analysis_tables.xlsx') # Arbitrary output name 

print(filenames[0])

for csvfilename in filenames:
    df = pd.read_csv("assets/"+csvfilename)
    df.to_excel(writer,sheet_name=csvfilename[:-4])
writer.save()
