import hashlib
import settings
import helpers
import database as db
import json
from flask import Flask, request, abort, jsonify

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'BumbleGum API: API KEY IS ' + settings.API_KEY, 200

@app.route('/numbers/get/', methods = ['GET']) #CALLBACK
def lincoln_numbers():
    """
    Space Lincolnshire Number Station. Irrelevant for right now, Left headless.

    TODO: Refluff and wire to a new system.
    """
    helpers.verify_api(request)
    db.conn.log_statement('numbers/get', json.dumps(request.args))
    return "", 200

@app.route('/bans/check/', methods = ['GET']) #BYPASS
def check_ban():
    helpers.check_allowed(True)
    #These are requested in a super weird format, *And are also our only form of connection log.*
    # ckey/compID/ip/record
    CON_EXEMPT = False
    if db.conn.check_exempt():
        CON_EXEMPT = True

    #Log Connection
    if request.args.get('record'):
        db.conn.log_connection()

    #Generate Return
    if CON_EXEMPT: #Exempt. Don't hit the DB again.
        return jsonify({'exempt': True}) #NOTE: This stuff looks legacy. Is it still meant to be functional? -F

    #Interrogate the ban table for the latest.

    return jsonify({'none': True})

@app.route('/versions/add/') #VOID
def track_version():
    """
    Track user version data for analytics purposes.
    Logs to feedback-version
    """
    helpers.check_allowed(True)
    db.conn.feedback_version()
    # db.conn.log_statement('versions/add', json.dumps(request.args))
    return "", 200

@app.route('/playerInfo/get/') #BYPASS
def get_player_info(): #see formats/playerinfo_get.json
    helpers.check_allowed(True)

    # db.conn.log_statement('playerInfo/get', json.dumps(request.args))
    return "", 200

@app.route('/playerInfo/getIPs/')
def get_player_ip_history():
    """
    Get the player's previous IP Addresses.

    TODO This format is gonna s u c k.
    """
    #Used at: player_stats.dm#102

    return "", 200

#Whatever crossed was doing last night.
if __name__ == '__main__':
    # pylint: disable=undefined-variable
    APP.debug = True
    APP.run()
