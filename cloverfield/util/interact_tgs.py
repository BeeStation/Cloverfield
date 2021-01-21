import base64
import requests
from flask import abort
from cloverfield.settings import cfg


#TGS4 Interaction code
#Due to all of this resetting after every request,
#mercifully we don't need to bother
#with token expiry.

#...I'm going to be proven wrong as hell aren't I.
#Y E P

BEARER_TOKEN = None #TGS4 Bearer Token.
user_agent = f"Cloverfield-API v{cfg['api_rev']}"

basic_header = {
        "Api": cfg["tgs"]["apiver"],
        "User-Agent": user_agent,
        "Content-Type": "application/json"
    }


#Module Private, if we have no bearer token, we need to get a new one.
def _update_bearer_token():
    global BEARER_TOKEN #pylint:disable=global-statement
    auth = base64.b64encode(f"{cfg['tgs']['user']}:{cfg['tgs']['pass']}".encode('ascii')).decode('ascii')

    url = cfg["tgs"]["host"]
    headers = basic_header.copy()
    headers.update({"Authorization": f"Basic {auth}"})
    response = requests.post(url, headers=headers)
    if(response.status_code > 299):
        abort(response.status_code) #Abort with the status code if not 2XX or informational.
    response_ct = response.json()
    BEARER_TOKEN = response_ct["bearer"]

def req_bearer(func):
    """
    Decorator for TGS Functions that require authentication.
    """
    def wrapper():
        global BEARER_TOKEN #pylint:disable=global-statement
        if(BEARER_TOKEN is None):
            _update_bearer_token()
        func()
        #FIXME expire tokens instead of spending them.
        BEARER_TOKEN = None #for now just void it to make my job easier.
    return wrapper

@req_bearer
def trigger_compile():
    headers = basic_header.copy()
    headers.update({
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "Instance": str(cfg["tgs"]["instance"])
    })
    url = f"{cfg['tgs']['host']}{'/DreamMaker'}"
    response = requests.put(url, headers=headers)
    if(response.status_code > 299):
        abort(response.status_code) #Abort with the status code if not 2XX or informational.
    return
