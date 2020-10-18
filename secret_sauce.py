import helpers
from flask import Blueprint, jsonify, request

api_secrets = Blueprint('secrets', __name__)

@api_secrets.route('/numbers/get/', methods = ['GET']) #CALLBACK
def lincoln_numbers():
    """
    Space Lincolnshire Number Station. Irrelevant for right now, Left headless.

    TODO: Refluff and wire to a new system.
    """
    helpers.verify_api(request)
    # db.conn.log_statement('numbers/get', json.dumps(request.args))
    return jsonify('OK')
