from libs.aiotranslator import Translator
from libs.aioconfigmanager import ConfigLoader
import os

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




