from logging import getLoggerClass
from google.cloud import translate_v3 as translate
import os
import time
from libs.aioconfigmanager import ConfigLoader
import os

TranslatorAgent = 'googleapi'
from_language = 'en'
to_language = 'ko'
GlossaryID = 'V4GB'


AppConfig = ConfigLoader()
Configuration = AppConfig.Config
AppLanguage  = Configuration['Document_Translator']['app_lang']
#tm = Configuration['Translator']['tm_path']
print(Configuration['Translator']['license_file'])
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = Configuration['Translator']['license_file']

def create_glossary(
	project_id="credible-bay-281107",
	input_uri="gs://nxvnbucket/DB_V4/AXE/AXEKR.csv",
	glossary_id="AXEKR_EN",
	timeout=180,
):
	"""
	Create a equivalent term sets glossary. Glossary can be words or
	short phrases (usually fewer than five words).
	https://cloud.google.com/translate/docs/advanced/glossary#format-glossary
	"""
	client = translate.TranslationServiceClient()

	# Supported language codes: https://cloud.google.com/translate/docs/languages
	source_lang_code = "en"
	target_lang_code = "ko"
	location = "us-central1"  # The location of the glossary
	#location = 'asia-southeast1'
	name = client.glossary_path(project_id, location, glossary_id)
	language_codes_set = translate.types.Glossary.LanguageCodesSet(
		language_codes=[source_lang_code, target_lang_code]
	)

	gcs_source = translate.types.GcsSource(input_uri=input_uri)

	input_config = translate.types.GlossaryInputConfig(gcs_source=gcs_source)

	glossary = translate.types.Glossary(
		name=name, language_codes_set=language_codes_set, input_config=input_config
	)


	parent = f"projects/{project_id}/locations/{location}"
	# glossary is a custom dictionary Translation API uses
	# to translate the domain-specific terminology.
	operation = client.create_glossary(parent=parent, glossary=glossary)

	result = operation.result(timeout)
	print('result', result)
	print("Created: {}".format(result.name))
	print("Input Uri: {}".format(result.input_config.gcs_source.input_uri))

def translate_text_with_glossary(
	text="YOUR_TEXT_TO_TRANSLATE",
	project_id="credible-bay-281107",
	
	glossary_id="AXEKR",
):
	"""Translates a given text using a glossary."""
	project_translate = "round-reality-294501"
	client = translate.TranslationServiceClient()
	location = "us-central1"
	parent = f"projects/{project_translate}/locations/{location}"
	
	glossary = client.glossary_path(
		project_id, "us-central1", glossary_id  # The location of the glossary
	)
	
	glossary_config = translate.TranslateTextGlossaryConfig(glossary=glossary)
	print('glossary_config', glossary_config)
	st = time.time()
	# Supported language codes: https://cloud.google.com/translate/docs/languages
	response = client.translate_text(
		request={
			"contents": text,
			"target_language_code": "ko",
			"source_language_code": "en",
			"parent": parent,
			"glossary_config": glossary_config,
		}
	)
	print('Get gloss',time.time()- st)
	print("Translated text: \n")
	for translation in response.glossary_translations:
		print(translation.translated_text)

def delete_glossary(
	project_id="credible-bay-281107", glossary_id="NXVNV4GB", timeout=180,
):
	"""Delete a specific glossary based on the glossary ID."""
	client = translate.TranslationServiceClient()

	name = client.glossary_path(project_id, "us-central1", glossary_id)

	operation = client.delete_glossary(name=name)
	result = operation.result(timeout)
	print("Deleted: {}".format(result.name))


def  list_glossaries(project_id="credible-bay-281107"):
	"""List Glossaries."""

	client = translate.TranslationServiceClient()

	location = "us-central1"

	parent = f"projects/{project_id}/locations/{location}"
	
	for glossary in client.list_glossaries(parent=parent):
		print("Name: {}".format(glossary.name.split('/')[-1]))
		
		print("Entry count: {}".format(glossary.entry_count))
		print("Input uri: {}".format(glossary.input_config.gcs_source.input_uri))

		# Note: You can create a glossary using one of two modes:
		# language_code_set or language_pair. When listing the information for
		# a glossary, you can only get information for the mode you used
		# when creating the glossary.d
		for language_code in glossary.language_codes_set.language_codes:
			print("Language code: {}".format(language_code))


#create_glossary()
list_glossaries()
my_gloss = 'General-DB'
#delete_glossary(glossary_id=my_gloss)
#create_glossary(glossary_id = my_gloss)
#create_glossary(input_uri="gs://nxvnbucket/DB/General/General.csv",	glossary_id= my_gloss)

#translate_text_with_glossary(['Use the active skill', 'Use the kaidan fruits.', 'Access to phantom of kaidan'])
#create_glossary(input_uri="gs://nxvnv4/DB/MSM.csv",	glossary_id="MSM")

#create_glossary()
#delete_glossary()
#translate_text_with_glossary('Groggy')
#asia-southeast1