import pandas as pd
my_l = ['a,b,c', 'd,e,f']

split = lambda x: x.split(',')

list_db = list(map(split, my_l))
#print(list_db)

upper_list = list(map(lambda x: list(map(lambda y: y.upper(), x)), list_db))

#print(upper_list)

new_df = pd.DataFrame(columns=['a', 'b', 'c'], data=upper_list)

print(new_df)

new_df.set_index('a')
new_df.reindex()

new_df = new_df.append({'a': 'F'}, ignore_index=True)

new_df = new_df.append({'a': 'F'}, ignore_index=True)

#print(new_df)

#translated = new_df.loc[new_df['a'] == 'F']
#index = translated.iloc[0]['c']

index = new_df.index
condition = new_df["a"] == "F"
apples_indices = index[condition]
apples_indices_list = apples_indices.tolist()[0]
new_df['b'][apples_indices_list]= 'E'
print(pd.isna(new_df['c'][apples_indices_list]))
#print(new_df)

#print(index)
'''
if len(translated) > 0:
    #print('TM translate', translated)
    return translated.iloc[0][self.from_language]
'''
#print(new_df)