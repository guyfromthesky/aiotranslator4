import pandas as pd
my_l = ['a,b,c', 'd,e,f']

split = lambda x: x.split()

list_db = list(map(split, my_l))
print(list_db)

upper_list = list(map(lambda x: list(map(lambda y: y.upper(), x)), list_db))

print(upper_list)

new_df = pd.DataFrame(columns=['my_column_name_1', 'my_column_name_2', 'my_column_name_3'], data=upper_list)
print(new_df)