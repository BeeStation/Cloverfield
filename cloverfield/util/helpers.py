from cloverfield.settings import *

import ipaddress
from flask import request, abort

import collections

#Reusables, primarily key authentication
def verify_api(packet):
    """
    Verify request API token is valid.
    """
    auth = packet.args.get('auth')
    if(not auth):
        abort(401)
    if(auth == API_KEY):
        return
    return abort(403)


def check_allowed(check_key=False, api_version=API_REV):
    """
    Configurable integrity check function.

    `packet` is the active request object.

    `check_key` (Default `False`), Verify API access is allowed.

    `api_version` (Default `API_REV`), Current allowed API verson.
    """
    if request.args.get('data_version') is None:
        abort(400)
    if(int(request.args.get('data_version')) != api_version):
        abort(400)
    if(check_key):
        verify_api(request)

def ip_getint(ip):
    """
    Get Int version of IP
    """
    try:
        return int(ipaddress.IPv4Address(ip))
    except:
        return 0

def ip_getstr(ip):
    """
    Get string version of IP
    """
    try:
        return str(ipaddress.IPv4Address(ip))
    except:
        return 0
