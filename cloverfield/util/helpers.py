from cloverfield.settings import cfg

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
    if(auth == cfg["keys"]["api_key"]):
        return
    return abort(403)


def check_allowed(check_key=False, api_version=cfg["api_rev"]):
    """
    Configurable integrity check function.

    `packet` is the active request object.

    `check_key` (Default `False`), Verify API access is allowed.

    `api_version` (Default `cfg["api_rev"]`), Current allowed API verson.
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
        return int(ip) #Try to typecast it. there's several reasons we might be passed a non-ip value here.

def ip_getstr(ip):
    """
    Get string version of IP
    """
    try:
        return str(ipaddress.IPv4Address(ip))
    except:
        return 0
