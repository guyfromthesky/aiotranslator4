from google.cloud import translate_v3 as translator
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r'C:\Users\evan\Desktop\Account\product_owner.json'

def create_glossary(
    project_id="credible-bay-281107",
    input_uri= r'gs://nxvnbucket/DB/SF2/SF2_db.csv',
    glossary_id="SF2",
    supported_language = ['en', 'ko'],
    location = "us-central1",
    timeout=180,
):
    """
    Create a equivalent term sets glossary. Glossary can be words or
    short phrases (usually fewer than five words).
    https://cloud.google.com/translate/docs/advanced/glossary#format-glossary
    """
    client = translator.TranslationServiceClient()

    name = client.glossary_path(project_id, location, glossary_id)
    
    language_codes_set = translator.types.Glossary.LanguageCodesSet(
        language_codes = supported_language
    )

    gcs_source = translator.types.GcsSource(input_uri=input_uri)

    input_config = translator.types.GlossaryInputConfig(gcs_source=gcs_source)

    glossary = translator.types.Glossary(
        name=name, language_codes_set=language_codes_set, input_config=input_config
    )

    parent = f"projects/{project_id}/locations/{location}"
    try:
        operation = client.create_glossary(parent=parent, glossary=glossary)
        return operation.result(timeout)
    except Exception as e:
        print('Error while uploading glossary:', e)
        return False


print(create_glossary())