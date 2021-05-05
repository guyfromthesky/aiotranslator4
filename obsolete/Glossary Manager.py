from google.cloud import translate_v3 as translate
import os
import time
from datetime import datetime

LOCATION = "us-central1"
#LOCATION = "asia-southeast1"
#LOCATION = "global"


cwd = os.path.dirname(os.path.realpath(__file__))
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]= 'C:\\Users\\evan\\Desktop\\Account\\product_owner.json'
print(cwd + '//json//my.json')

def create_glossary(
	project_id="credible-bay-281107",
	input_uri="gs://nxvnbucket/DB/V4/NXVNV4GB.csv",
	glossary_id="NXVNV4GB",
	timeout=180,
	prefer_language = 'ko'
):
	"""
	Create a equivalent term sets glossary. Glossary can be words or
	short phrases (usually fewer than five words).
	https://cloud.google.com/translate/docs/advanced/glossary#format-glossary
	"""
	client = translate.TranslationServiceClient()

	# Supported language codes: https://cloud.google.com/translate/docs/languages
	if prefer_language =='ko':
		source_lang_code = "ko"
		target_lang_code = "en"
	else:
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

	parent = f"projects/{project_id}/locations/{LOCATION}"
	# glossary is a custom dictionary Translation API uses
	# to translate the domain-specific terminology.
	operation = client.create_glossary(parent=parent, glossary=glossary)

	result = operation.result(timeout)
	print("Created: {}".format(result.name))
	print("Input Uri: {}".format(result.input_config.gcs_source.input_uri))

def translate_text_with_glossary(
	text="YOUR_TEXT_TO_TRANSLATE",
	project_id="credible-bay-281107",
	glossary_id="General",
):
	"""Translates a given text using a glossary."""
	
	client = translate.TranslationServiceClient()
	location = "us-central1"
	parent = f"projects/{project_id}/locations/{LOCATION}"
	print('parent', parent)
	glossary = client.glossary_path(project_id, LOCATION, glossary_id)
	#print('glossary', glossary)
	glossary_config = translate.TranslateTextGlossaryConfig(glossary=glossary)
	st = time.time()
	#print('glossary_config', glossary_config)
	# Supported language codes: https://cloud.google.com/translate/docs/languages
	
	response = client.translate_text(
		request={
			"contents": [text],
			"target_language_code": "ko",
			"source_language_code": "en-US",
			"parent": parent,
			"mime_type": "text/plain",
			"glossary_config": glossary_config,
		}
	)
	print('response', response)
	for translation in response.glossary_translations:
		print(format(translation.translated_text))
		#print('unescape',html.unescape(translation.translated_text))

def delete_glossary(
	project_id="credible-bay-281107", glossary_id="NXVNV4GB", timeout=180,
):
	"""Delete a specific glossary based on the glossary ID."""
	client = translate.TranslationServiceClient()

	name = client.glossary_path(project_id, "us-central1", glossary_id)

	operation = client.delete_glossary(name=name)
	result = operation.result(timeout)
	print("Deleted: {}".format(result.name))


def get_glossary(
	project_id="credible-bay-281107", glossary_id="V4GB", timeout=180,
):

	
	client = translate.TranslationServiceClient()
	name = client.glossary_path(project_id, LOCATION, glossary_id)
	glossary = client.get_glossary(name = name)
		
	print("Name: {}".format(glossary.name))
	print("Entry count: {}".format(glossary.entry_count))
	print("Input uri: {}".format(glossary.input_config.gcs_source.input_uri))

	# Note: You can create a glossary using one of two modes:
	# language_code_set or language_pair. When listing the information for
	# a glossary, you can only get information for the mode you used
	# when creating the glossary.
	for language_code in glossary.language_codes_set.language_codes:
		print("Language code: {}".format(language_code))
	#print(glossaries)

def get_glossary_path(
	project_id="credible-bay-281107", glossary_id="V4GB", timeout=180,
):

	
	client = translate.TranslationServiceClient()
	name = client.glossary_path(project_id, LOCATION, glossary_id)
	glossary = client.get_glossary(name = name)
	uri = glossary.input_config.gcs_source.input_uri
	temp = uri.split('nxvnbucket/')[-1]
	print(temp)
	Outputdir = os.path.dirname(uri)
	print('Outputdir', Outputdir)
	baseName = os.path.basename(uri)
	print('baseName', baseName)
	#sourcename, ext = os.path.splitext(baseName)


def list_glossaries(project_id="credible-bay-281107"):
	"""List Glossaries."""

	client = translate.TranslationServiceClient()

	location = "us-central1"

	parent = f"projects/{project_id}/locations/{LOCATION}"

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

#list_glossaries()

delete_glossary(glossary_id = 'General')
create_glossary(input_uri="gs://nxvnbucket/DB/General/General.csv",	glossary_id="General-DB")

#translate_text_with_glossary('Quest')

#create_glossary(input_uri="gs://nxvnbucket/DB/KWKR/KWKR.csv",	glossary_id="KWKR")

#translate_text_with_glossary(['Groggy', 'Test', 'Happy'])
#delete_glossary(glossary_id = 'V4GB')
#create_glossary(input_uri="gs://nxvnbucket/DB/V4/NXVN_V4GB.csv", glossary_id="V4GB_TEST")
#delete_glossary(glossary_id = 'MSM')
#create_glossary(input_uri="gs://nxvnbucket/DB/MSM/NXVN_MSM.csv", glossary_id='MSM_TEST', prefer_language = 'en')
#list_glossaries()
#create_glossary()
#delete_glossary()

#asia-southeast1
#NXVNV4GB
#MSMDB
#delete_glossary(glossary_id = 'NXVNV4GB')

#get_glossary_path(glossary_id='V4GB')



# Then do other things...
#blob2 = bucket.blob('DB/V4/NXVN_V4GB.csv')
#blob = bucket.blob('DB/V4/Test.txt')
#blob.upload_from_string('New contents!')
#blob.upload_from_string('New contents!')
#bucket.delete_blob(blob_name = 'DB/V4/Test.txt')


#blob2.upload_from_filename(filename='path.txt')
#blob2.delete_blob()
#print(blob2.download_as_string())

#list_glossaries()
'''
from google.cloud import storage
client = storage.Client()

# https://console.cloud.google.com/storage/browser/[bucket-id]/
bucket = client.get_bucket('nxvnbucket')
blob = bucket.get_blob('DB/MSM/MSM.csv')
#bucket.delete_blob(blob_name = 'DB/V4/NXVN_OHJ.csv')
#blob.upload_from_filename(filename='C:\\Users\\evan\\OneDrive - NEXON COMPANY\\AIO Translator 3.0\\AIO Translator 3.1.c\\NXVN_OHJ.csv')

#print(DB)



print(blob.download_as_text())
'''
'''
blob.upload_from_string('New contents!')
blob2 = bucket.blob('remote/path/storage.txt')
blob2.upload_from_filename(filename='/local/path.txt')
'''