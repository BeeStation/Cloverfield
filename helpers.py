import settings
import ipaddress
from flask import request, abort

#Reusables, primarily key authentication
def verify_api(packet):
    """
    Verify request API token is valid.
    """
    auth = packet.args.get('auth')
    if(not auth):
        abort(401)
    if(auth == settings.API_KEY):
        return
    return abort(403)


def check_allowed(check_key=False, api_version=1):
    """
    Configurable integrity check function.

    `packet` is the active request object.

    `check_key` (Default `False`), Verify API access is allowed.

    `api_version` (Default `1`), Current allowed API verson.
    """
    if(int(request.args.get('data_version')) != api_version):
        abort(400)
    if(check_key):
        verify_api(request)

def ip_getint(ip):
    return int(ipaddress.IPv4Address(ip))

def ip_getstr(ip):
    return str(ipaddress.IPv4Address(ip))
