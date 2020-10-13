import hashlib
import settings
import helpers
from flask import Flask, request, abort, jsonify

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'BumbleGum API: API KEY IS ' + settings.API_KEY

@app.route('/numbers/get/', methods = ['GET'])
def lincoln_numbers():
    helpers.verify_api(request)

    return "", 200

@app.route('/bans/check/', methods = ['GET'])
def check_ban():
    helpers.verify_api(request)
    return "", 200

@app.route('/versions/add/')
def track_version():
    """
    Track user version data for analytics purposes.

    TODO Actually wire up anything here. For now this just blindly accepts data so the proc doesn't fail.
    """
    return "", 200

@app.route('/playerInfo/get/')
def get_player_info(): #see formats/playerinfo_get.json
    pass

@app.route('/playerInfo/getIPs/')
def get_player_ip_history():
    """
    Get the player's previous IP Addresses.

    TODO This format is gonna s u c k.
    """
    #Used at: player_stats.dm#102

    pass

#Whatever crossed was doing last night.
if __name__ == '__main__':
    # pylint: disable=undefined-variable
    APP.debug = True
    APP.run()