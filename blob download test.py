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
tm = Configuration['translation_memory']['path']
print(Configuration['license_file']['path'])
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = Configuration['license_file']['path']

GlossaryID = Configuration['glossary_id']['value']
print(tm)

MyTranslator = Translator()

#download_blob(self, bucket_id, blob_id, download_path):
file = 'C:\\Users\\evan\\Documents\\GitHub\\aiotranslator4\\test files\\V4.csv'
d_file = 'C:\\Users\\evan\\Documents\\GitHub\\aiotranslator4\\test files\\V4_test.csv'
MyTranslator.upload_blob(blob_id = 'test/test.csv', upload_path = file)

MyTranslator.download_blob(blob_id = 'test/test.csv', download_path = d_file)


