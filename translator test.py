#from libs.aiotranslator_v2 import Translator
from libs.aioconfigmanager import ConfigLoader
import os

TranslatorAgent = 'googleapi'
from_language = 'en'
to_language = 'ko'
GlossaryID = 'V4GB'

import pickle



AppConfig = ConfigLoader()
Configuration = AppConfig.Config
#AppLanguage  = Configuration['Document_Translator']['app_lang']
#tm = Configuration['Translator']['tm_path']
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r'C:\Users\evan\Desktop\Account\nwv-user.json'

GlossaryID = 'TW2RJP'
#print(tm)

test_text = 'Use the 액티브 스킬'

def translate_text(text):
    """Translates text into the target language.

    Target must be an ISO 639-1 language code.
    See https://g.co/cloud/translate/v2/translate-reference#supported_languages
    """
 
    import six
    from google.cloud import translate_v2 as translate

    translate_client = translate.Client()

    if isinstance(text, six.binary_type):
        text = text.decode("utf-8")

    # Text can also be a sequence of strings, in which case this method
    # will return a sequence of results for each text.
    result = translate_client.translate(text, target_language='ko', source_language='en')

    print(u"Text: {}".format(result["input"]))
    print(u"Translation: {}".format(result["translatedText"]))
    #print(u"Detected source language: {}".format(result["detectedSourceLanguage"]))

translate_text('빌드(앱) 정상 설치 확인')