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
tm = Configuration['TranslationMemory']['path']
print(Configuration['License_File']['path'])
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = Configuration['License_File']['path']

GlossaryID = Configuration['Glossary_ID']['value']
print(tm)

MyTranslator = Translator(From_Language = 'ko', To_Language = 'en', GlossaryID =  GlossaryID, ProactiveTMTranslate= True, TM_Path=tm)
#MyTranslator.temporary_tm = MyTranslator.TranslationMemory
#MyTranslator.temporary_tm['en'] = MyTranslator.temporary_tm['en']
#MyTranslator.append_translation_memory()
MyTranslator.OptimizeTranslationMemory()
#Source_Text = '201211_V4_GL19.1_데이터패치배포_3차'.lower()
#print('Translated', MyTranslator.MemoryTranslate('201211_V4_GL19.1_데이터패치배포_3차'))
#print(MyTranslator.translate('201211_V4_GL19.1_데이터패치배포_3차'))
#MyTranslator.Simple_Optmize()
#MyTranslator.AppendTranslationMemory()
#MyTranslator.RefreshTranslationMemory()
#index = MyTranslator.KO.index(Source_Text)
#print('Source_Text', Source_Text)
#print('index', index)