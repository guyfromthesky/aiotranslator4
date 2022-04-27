import pandas as pd

mydict = {
    'EN': ['abc', 'xyz', 'ppp' , 'aaa', 'qqq', 'www', 'eee'],
    'KO': ['뮻', '툨', 'ㅔㅔㅔ', 'ㅁㅁㅁ', 'ㅂㅂㅂ', 'ㅈㅈㅈ', 'ㄷㄷㄷ',]
}

df = pd.DataFrame(mydict)

ROW_LIMIT = 2

df_list = []

for x in range(int(len(df)/ROW_LIMIT)+1):
    #start_row = ROW_LIMIT * x
    #end_row = ROW_LIMIT * (x + 1) - 1
    new_df = df.iloc[ROW_LIMIT * x:ROW_LIMIT * (x + 1) - 1]
    print(new_df)
    df_list.append(new_df)
