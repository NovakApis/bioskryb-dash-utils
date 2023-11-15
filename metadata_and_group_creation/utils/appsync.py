import base64
import hashlib
import hmac
import json
import pprint

import boto3
import requests


def call_appsync(appsync_endpoint_url, access_token, json_as_str) -> dict:
    """
    Calls the appsync endpoint with the given access token and json query

    Args:
        appsync_endpoint_url (str): The appsync endpoint url
        access_token (str): The access token
        json_as_str (str): The json query (in appsync string format)

    Returns:
        response (dict): The response from the appsync endpoint
    """
    session = requests.Session()
    response = session.request(
        url=appsync_endpoint_url,
        method="POST",
        headers={"authorization": access_token},
        json={"query": json_as_str},
    )
    if response.status_code != 200:  # TODO : make this more robust
        # print(response.text)
        raise Exception(response.text)
    return response.json()


def get_user_access_token(app_sync_user: dict, secret_hash: bool = False) -> str:
    """
    Gets the user access token for the given appsync user
    Args:
        app_sync_user (dict): The appsync user
        secret_hash (bool): Whether to use secret hash or not

    Returns:
        access_token (str): The access token
    """
    cognito_client = boto3.client("cognito-idp")
    username = app_sync_user["username"]
    app_client_id = app_sync_user["clientId"]
    auth_paramaters = {
        "USERNAME": app_sync_user["username"],
        "PASSWORD": app_sync_user["password"],
    }
    if secret_hash:
        key = app_sync_user["appClientSecret"]
        message = bytes(username + app_client_id, "utf-8")
        key = bytes(key, "utf-8")
        secret_hash = base64.b64encode(
            hmac.new(key, message, digestmod=hashlib.sha256).digest()
        ).decode()
        auth_paramaters["SECRET_HASH"] = secret_hash
    response = cognito_client.initiate_auth(
        ClientId=app_sync_user["clientId"],
        AuthFlow="USER_PASSWORD_AUTH",
        AuthParameters=auth_paramaters,
    )

    return response["AuthenticationResult"]["AccessToken"]


def fetch_table_data_from_appsync(
    project_id: str, app_sync_endpoint: str, app_sync_user: dict
) -> dict:
    """
    Fetches the table data from the appsync endpoint

    Args:
        project_id (str): The project id
        app_sync_endpoint (str): The appsync endpoint url
        app_sync_user (dict): The appsync user

    Returns:
        response (dict): The response from the appsync endpoint with biosample data
    """
    token = get_user_access_token(app_sync_user)
    query = f"""
        query MyQuery {{
            getProject(id: "{project_id}") {{
                biosampleMetadataColumns
                biosamples {{
                    items {{
                        biosampleName
                        fastqValidationStatus
                        size
                        r1FastqTotalReads
                        r2FastqTotalReads
                        r1FastqLength
                        created
                        lotId
                        metadata
                    }}
                }}
            }}
        }}
    """
    response = call_appsync(app_sync_endpoint, token, query)["data"]["getProject"]
    return response
