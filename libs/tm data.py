import pickle
import pandas as pd
import numpy as np

TM_Path = '\\\\share\\\Share Folder\\VN Mobile QA3\\V4GB\\Database\\V4GB.pkl'
GlossaryID = "V4"

with open(TM_Path, 'rb') as pickle_load:
	
	all_tm = pickle.load(pickle_load)

	if isinstance(all_tm, dict):

		# TM format v4
		if GlossaryID in all_tm:
			print('TM v4')
			TranslationMemory = all_tm[GlossaryID]
		# TM format v3
		elif 'EN' in all_tm:
			print('TM v3')
			#data_tuples = list(zip(all_tm['EN'],all_tm['KO']))
			
			TranslationMemory = pd.DataFrame()
			TranslationMemory['en'] = all_tm['EN']
			TranslationMemory['en'] = TranslationMemory['en'].str.lower()
			TranslationMemory['ko'] = all_tm['KO']
			TranslationMemory['ko'] = TranslationMemory['ko'].str.lower()

	elif isinstance(all_tm, list):
		print('TM v2')
		#Consider drop support
		TranslationMemory = pd.DataFrame()
		for Pair in all_tm:
			new_row = {'en': Pair[1], 'ko':Pair[0],}
			TranslationMemory = TranslationMemory.append(new_row, ignore_index=True)
To_Language = 'ko'
From_Language = 'en'
source_text = 'Coupon test'
source_text = source_text.lower()

if len(TranslationMemory) > 0:
	#translated = TranslationMemory[To_Language].where(TranslationMemory[From_Language] == source_text)[0]
	translated = TranslationMemory.loc[TranslationMemory[From_Language] == source_text]
	print(translated.iloc[0]['ko'])
	
	#print(translated[To_Language][0])
	if isinstance(translated, str):
		print(translated)
