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
def access_secret_version(project_id, secret_id, version_id="latest"):
    """
    Accesses the payload of the given secret version.
    """
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")