
from google.cloud import secretmanager
from google.oauth2 import service_account
import json
import configparser

def cfms_to_rating(cfms):
    if cfms > 80:
        return 'Strong Buy'
    elif cfms > 60:
        return 'Buy'
    elif cfms > 40:
        return 'Hold'
    elif cfms > 20:
        return 'Caution'
    elif cfms <= 20:
        return 'Sell Immediately'
    else:
        return '<NA>'
    
# FUNCTION TO ACCESS A SECRET FROM GOOGLE SECRET MANAGER
def access_cred_gc_secret_manager(project_id, secret_id, version_id="latest"):
    """
    Accesses the payload of the given secret version.
    """

    # Scopes required for Google Sheets and other Google services
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    # Initialize the Secret Manager client
    client = secretmanager.SecretManagerServiceClient()
    # Construct the secret version resource name
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    # Fetch the secret version
    response = client.access_secret_version(request={"name": name})
    # Decode the secret payload to UTF-8
    secret_payload = response.payload.data.decode("UTF-8")
    # Print secret payload for debugging
    print("Secret Payload:", secret_payload)
    # Parse the JSON string directly
    credentials_dict = json.loads(secret_payload)
    # Create credentials from the parsed dictionary
    credentials = service_account.Credentials.from_service_account_info(credentials_dict, scopes=scopes)
    
    return credentials