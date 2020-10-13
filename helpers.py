import settings
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

