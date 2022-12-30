import unittest
from libs.aiotranslator import Translator
from libs.aioconfigmanager import ConfigLoader
import os

AppConfig = ConfigLoader()
Configuration = AppConfig.Config
AppLanguage  = Configuration['Document_Translator']['app_lang']
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = Configuration['Translator']['license_file']

tm = Configuration['Translator']['translation_memory']

GlossaryID = Configuration['Translator']['glossary_id']

class translate_test(unittest.TestCase):
	def __init__(self):
		self.my_translator = Translator(From_Language = 'en', To_Language = 'ko', GlossaryID =  'AXEKR', ProactiveTMTranslate= True, TM_Path=tm)

	def test_simpe_sentence(self):
		_translation = self.my_translator.translate('Hello')
		self.assertEqual('foo'.upper(), 'FOO')

	def test_isupper(self):
		self.assertTrue('FOO'.isupper())
		self.assertFalse('Foo'.isupper())

	def test_split(self):
		s = 'hello world'
		self.assertEqual(s.split(), ['hello', 'world'])
		# check that s.split fails when the separator is not a string
		with self.assertRaises(TypeError):
			s.split(2)

if __name__ == '__main__':
	unittest.main()