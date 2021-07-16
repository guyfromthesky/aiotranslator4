from google.cloud import translate_v3 as translate
import os
import time
from datetime import datetime

cwd = os.path.dirname(os.path.realpath(__file__))
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]= cwd + '/json/Admin.json'
print(cwd + '//json//my.json')
def create_glossary(
	project_id="credible-bay-281107",
	input_uri="gs://nxvnbucket/DB/V4/NXVNV4GB.csv",
	glossary_id="NXVNV4GB",
	timeout=180,
):
	"""
	Create a equivalent term sets glossary. Glossary can be words or
	short phrases (usually fewer than five words).
	https://cloud.google.com/translate/docs/advanced/glossary#format-glossary
	"""
	client = translate.TranslationServiceClient()

	# Supported language codes: https://cloud.google.com/translate/docs/languages
	source_lang_code = "ko"
	target_lang_code = "en"
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
	print("Created: {}".format(result.name))
	print("Input Uri: {}".format(result.input_config.gcs_source.input_uri))

def translate_text_with_glossary(
	text="YOUR_TEXT_TO_TRANSLATE",
	project_id="credible-bay-281107",
	glossary_id="MSM",
):
	"""Translates a given text using a glossary."""
	
	client = translate.TranslationServiceClient()
	location = "us-central1"
	parent = f"projects/{project_id}/locations/{location}"

	glossary = client.glossary_path(
		project_id, "us-central1", glossary_id  # The location of the glossary
	)
	
	glossary_config = translate.TranslateTextGlossaryConfig(glossary=glossary)
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
		print("\t {}".format(translation.translated_text))

def delete_glossary(
	project_id="credible-bay-281107", glossary_id="NXVNV4GB", timeout=180,
):
	"""Delete a specific glossary based on the glossary ID."""
	client = translate.TranslationServiceClient()

	name = client.glossary_path(project_id, "us-central1", glossary_id)

	operation = client.delete_glossary(name=name)
	result = operation.result(timeout)
	print("Deleted: {}".format(result.name))


def get_glossary(glossaryID, timeout=180,):

	glossaries = self.Client.list_glossaries(glossaryID)

	print(glossaries)


def list_glossaries(project_id="credible-bay-281107"):
	"""List Glossaries."""

	client = translate.TranslationServiceClient()

	location = "us-central1"

	parent = f"projects/{project_id}/locations/{location}"

	# Iterate over all results
	for glossary in client.list_glossaries(parent=parent):
		print("Name: {}".format(glossary.name))
		print("Entry count: {}".format(glossary.entry_count))
		print("Input uri: {}".format(glossary.input_config.gcs_source.input_uri))

		# Note: You can create a glossary using one of two modes:
		# language_code_set or language_pair. When listing the information for
		# a glossary, you can only get information for the mode you used
		# when creating the glossary.
		for language_code in glossary.language_codes_set.language_codes:
			print("Language code: {}".format(language_code))

list_glossaries()

#delete_glossary(glossary_id = 'OH')
#create_glossary(input_uri="gs://nxvnbucket/DB/OH/OH.csv",	glossary_id="OH")

#translate_text_with_glossary(['Groggy', 'Test', 'Happy'])
#create_glossary(input_uri="gs://nxvnv4/DB/MSM.csv",	glossary_id="MSM")

#create_glossary()
#delete_glossary()
#translate_text_with_glossary('Groggy')
#asia-southeast1