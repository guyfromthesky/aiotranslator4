from libs.aiotranslator_v2 import Translator
from libs.aioconfigmanager import ConfigLoader
import os
from sys import getsizeof

TranslatorAgent = 'googleapi'
from_language = 'en'
to_language = 'ko'
GlossaryID = 'V4GB'

import pickle



AppConfig = ConfigLoader()
Configuration = AppConfig.Config
AppLanguage  = Configuration['Document_Translator']['app_lang']
tm = Configuration['translation_memory']['path']
print(Configuration['license_file']['path'])
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = Configuration['license_file']['path']

GlossaryID = Configuration['glossary_id']['value']
print(tm)

MyTranslator = Translator(from_language = 'ko', to_language = 'en', glossary_id =  GlossaryID, proactive_memory_translate= True, tm_path=tm)
#MyTranslator.temporary_tm = MyTranslator.TranslationMemory
#MyTranslator.temporary_tm['en'] = MyTranslator.temporary_tm['en']
#MyTranslator.append_translation_memory()
#MyTranslator.OptimizeTranslationMemory()
text = 'Coupon test'
source_text = text.lower()
'''
MyTranslator.TranslationMemory = MyTranslator.TranslationMemory.set_index([MyTranslator.From_Language])
translated = MyTranslator.TranslationMemory.loc[source_text][MyTranslator.To_Language]
print(translated)
'''

#text = MyTranslator.TranslationMemory[MyTranslator.TranslationMemory[MyTranslator.From_Language].str.match(source_text)]
#print(len(MyTranslator.TranslationMemory))
#text = MyTranslator.TranslationMemory.loc[MyTranslator.TranslationMemory[MyTranslator.From_Language] == source_text]

#print(text)
'''
for index, row  in MyTranslator.TranslationMemory.iterrows():
	if index < 100:
		print(row[MyTranslator.From_Language])
		if source_text == row[MyTranslator.From_Language]:
			print('Result: ', row[MyTranslator.To_Language])
			break
print('Not found')
'''

print(MyTranslator.memory_translate(text))
#print(MyTranslator.translate(text))
#Source_Text = '201211_V4_GL19.1_데이터패치배포_3차'.lower()
#print('Translated', MyTranslator.MemoryTranslate('201211_V4_GL19.1_데이터패치배포_3차'))
#print(MyTranslator.translate('201211_V4_GL19.1_데이터패치배포_3차'))
#MyTranslator.Simple_Optmize()
#MyTranslator.AppendTranslationMemory()
#MyTranslator.RefreshTranslationMemory()
#index = MyTranslator.KO.index(Source_Text)
#print('Source_Text', Source_Text)
#print('index', index)