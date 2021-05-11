import pandas as pd
import numpy as np
from sys import getsizeof

df = pd.DataFrame()

keya = 'A'
keyB = 'B'
a_string = 'Come'
new_row = {keyB:a_string, keya:87,}
#append row to the dataframe
df = df.append(new_row, ignore_index=True)

df = df.append(new_row, ignore_index=True)

df = df.append(new_row, ignore_index=True)


result = df[keya].where(df[keyB] == a_string)[0]


print(result)

