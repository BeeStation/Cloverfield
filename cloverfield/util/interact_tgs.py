import requests
import base64
import json
from cloverfield.settings import cfg
from flask import abort

#TGS4 Interaction code
#Due to all of this resetting after every request,
#mercifully we don't need to bother
#with token expiry.

#...I'm going to be proven wrong as hell aren't I.

bearer_token = None #TGS4 Bearer Token.
user_agent = f"Cloverfield-API v{cfg['api_rev']}"

basic_header = {
        "Api": cfg["tgs"]["apiver"],
        "User-Agent": user_agent,
        "Content-Type": "application/json"
    }


#Module Private, if we have no bearer token, we need to get a new one.
def _update_bearer_token():
    global bearer_token
    auth = base64.b64encode(f"{cfg['tgs']['user']}:{cfg['tgs']['pass']}".encode('ascii')).decode('ascii')

    url = cfg["tgs"]["host"]
    headers = basic_header.copy()
    headers.update({"Authorization": f"Basic {auth}"})
    response = requests.post(url, headers=headers)
    if(response.status_code > 299):
        abort(response.status_code) #Abort with the status code if not 2XX or informational.
    response_ct = response.json()
    bearer_token = response_ct["bearer"]

def req_bearer(func):
    """
    Decorator for TGS Functions that require authentication.
    """
    def wrapper():
        if(bearer_token is None):
            _update_bearer_token()
        func()
    return wrapper

@req_bearer
def trigger_compile():
    headers = basic_header.copy()
    headers.update({
        "Authorization": f"Bearer {bearer_token}",
        "Instance": str(cfg["tgs"]["instance"])
    })
    url = f"{cfg['tgs']['host']}{'/DreamMaker'}"
    response = requests.put(url, headers=headers)
    if(response.status_code > 299):
        abort(response.status_code) #Abort with the status code if not 2XX or informational.
    return
