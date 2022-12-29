from google.cloud import translate_v3 as translator
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r'C:\Users\evan\Desktop\Account\product_owner.json'

def delete_glossary(
    project_id="YOUR_PROJECT_ID",
    glossary_id="YOUR_GLOSSARY_ID",
    timeout=180,
):
    """Delete a specific glossary based on the glossary ID."""
    client = translator.TranslationServiceClient()

    name = client.glossary_path(project_id, "us-central1", glossary_id)

    operation = client.delete_glossary(name=name)
    result = operation.result(timeout)
    print("Deleted: {}".format(result.name))

print(delete_glossary())