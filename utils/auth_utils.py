
import requests
import json
import datetime
from dash import html
import dash_bootstrap_components as dbc
import os
import bfabric
from bfabric import BfabricAuth
from bfabric import BfabricClientConfig


VALIDATION_URL = "https://fgcz-bfabric.uzh.ch/bfabric/rest/token/validate?token="
HOST = "fgcz-bfabric.uzh.ch"

def token_to_data(token: str) -> str: 
    
    if not token:
        return None

    validation_url = VALIDATION_URL + token
    res = requests.get(validation_url, headers={"Host": HOST})
    
    if res.status_code != 200:
        res = requests.get(validation_url)
    
        if res.status_code != 200:
            return None
    try:
        master_data = json.loads(res.text)
    except:
        return None
    
    if True: 

        userinfo = json.loads(res.text)
        expiry_time = userinfo['expiryDateTime']
        current_time = datetime.datetime.now()
        five_minutes_later = current_time + datetime.timedelta(minutes=5)

        # Comparing the parsed expiry time with the five minutes later time

        if not five_minutes_later <= datetime.datetime.strptime(expiry_time, "%Y-%m-%d %H:%M:%S"):
            return "EXPIRED"

        envioronment_name = str(userinfo['environment']).strip().lower()
        environment_dict = {"production":"https://fgcz-bfabric.uzh.ch/bfabric","prod":"https://fgcz-bfabric.uzh.ch/bfabric","test":"https://fgcz-bfabric-test.uzh.ch/bfabric"}
        

        token_data = dict(
            environment = userinfo['environment'],
            user_data = userinfo['user'],
            token_expires = expiry_time,
            entity_id_data = userinfo['entityId'],
            entityClass_data = userinfo['entityClassName'],
            webbase_data = environment_dict[envioronment_name],
            application_params_data = {},
            application_data = str(userinfo['applicationId']),
            userWsPassword = userinfo['userWsPassword']
        )

        return json.dumps(token_data)
    

def token_response_to_bfabric(token_response: dict) -> str:

    bfabric_auth = BfabricAuth(login=token_response.get('user_data'), password=token_response.get('userWsPassword'))
    bfabric_client_config = BfabricClientConfig(base_url=token_response['webbase_data'])

    bfabric_wrapper = bfabric.Bfabric(config=bfabric_client_config, auth=bfabric_auth)

    return bfabric_wrapper


def entity_data(token_data: dict) -> str: 

    """
    This function takes in a token from B-Fabric, and returns the entity data for the token.
    Edit this function to change which data is stored in the browser for this entity.
    """

    entity_class_map = {
        "Run": "run",
        "Sample": "sample",
        "Project": "container",
        "Order": "container",
        "Container": "container",
        "Plate": "plate"
    }

    if not token_data:
        return None

    wrapper = token_response_to_bfabric(token_data)
    entity_class = token_data.get('entityClass_data', None)
    endpoint = entity_class_map.get(entity_class, None)
    entity_id = token_data.get('entity_id_data', None)

    if wrapper and entity_class and endpoint and entity_id:
        entity_data_dict = wrapper.read(endpoint=endpoint, obj={"id": entity_id}, max_results=None)[0]
        
        if entity_data_dict:
            json_data = json.dumps({
                "createdby": entity_data_dict.get("createdby"),
                "created": entity_data_dict.get("created"),
                "modified": entity_data_dict.get("modified"),
                "name": entity_data_dict.get("name"),
            })
            return json_data
        else:
            return None
    else:
        return None



def send_bug_report(token_data, entity_data, description):

    mail_string = f"""
        BUG REPORT FROM BARCODE DASHBOARD
        \n\n
        token_data: {token_data} \n\n 
        entity_data: {entity_data} \n\n
        description: {description} \n\n
        sent_at: {datetime.datetime.now()} \n\n
    """

    # mail = f"""
    #     echo "{mail_string}" | mail -s "Bug Report" griffin@gwcustom.com
    # """

    mail = f"""
        echo "{mail_string}" | mail -s "Bug Report" gwtools@fgcz.system
    """


    print("MAIL STRING:")
    print(mail_string)

    print("MAIL:")
    print(mail)

    os.system(mail)

    return True