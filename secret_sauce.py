import helpers
import random
from callback import hub_callback
from flask import Blueprint, jsonify, request
import asyncio

api_secrets = Blueprint('secrets', __name__)

@api_secrets.route('/numbers/get/', methods = ['GET']) #CALLBACK
def lincoln_numbers():
    """
    Space Lincolnshire Number Station. Irrelevant for right now, Left headless.

    TODO: Refluff and wire to a new system.
    """
    helpers.verify_api(request)
    numbas:list = list()
    for x in range(25): #pylint: disable=unused-variable
        numbas.append(random.randint(1,99))
    numbas: str = " ".join(map(str, numbas)) #The server wants these numbers in the absolute dumbest format I've ever fucking seen...
    asyncio.run(hub_callback('lincolnshire_numbers',{"numbers": numbas}, secure=True))
    # db.conn.log_statement('numbers/get', json.dumps(request.args))
    return jsonify('OK')
