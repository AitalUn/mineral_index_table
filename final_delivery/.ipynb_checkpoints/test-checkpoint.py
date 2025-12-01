import pandas as pd

df = pd.read_excel('indicies.xlsx')
count = pd.notna(df['LANDSAT-89 OLITIRS']).sum()
print(count)