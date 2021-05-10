import pandas as pd
import numpy as np
from sys import getsizeof

df = pd.DataFrame()

print(getsizeof(df))


print(df)
keya = 'A'
keyB = 'B'
new_row = {keyB:'Geo', keya:87,}
#append row to the dataframe
df.append(new_row, ignore_index=True)

df.append(new_row, ignore_index=True)

df.append(new_row, ignore_index=True)


result = df['A'].where(df['B'] == 'Geo')


print(result)

