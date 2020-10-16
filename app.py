import hashlib
import settings
import helpers
import neodb as db
import sqlalchemy
from neodb import Session, Player, Ban, sessionmaker
from statics.database import FLAG_EXEMPT
import json
from flask import Flask, request, abort, jsonify
from orm_serializers import JSON_Goon
import datetime

app = Flask(__name__)
app.json_encoder = JSON_Goon #Overwrite the default encoder to serialize bans.

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
    # db.conn.log_statement('numbers/get', json.dumps(request.args))
    return "", 200

@app.route('/bans/check/', methods = ['GET']) #BYPASS
def check_ban():
    helpers.check_allowed(True)
    #These are requested in a super weird format, *And are also our only form of connection log.*
    # ckey/compID/ip/record
    session: sqlalchemy.orm.Session = Session()
    player: Player = db.Player.from_ckey(request.args.get('ckey'), session)
    if player is None: #Player doesn't exist, construct them before continuing.
        player = helpers.construct_player(session)
        session.add(player)

    #Log Connection
    helpers.log_connection(session)

    #Generate Return
    if player.flags & FLAG_EXEMPT:#Exempt. We're done here.
        session.commit()
        return jsonify({'exempt': True}) #NOTE: This stuff looks legacy. Is it still meant to be functional? -F

    #Interrogate the ban table for the latest.

    #Update their previous data.
    if request.args.get('ip'):
        player.last_ip = helpers.ip_getint(request.args.get('ip'))
    if request.args.get('compID'):
        player.last_cid = request.args.get('compID')
    player.lastseen = datetime.datetime.utcnow()

    if len(player.bans):
        x: list = player.bans.copy()
        x.insert(0, len(player.bans)+1)
        session.commit()
        return jsonify(x) #This is so fucking stupid.
        #Returned format is fucking
        #[1,{ban},{ban}]... You have len() in byond. *just get the last entry in the fucking list*


    #Nothin' of note. Close her up.
    session.commit()
    return jsonify({'none': True})

@app.route('/versions/add/') #VOID
def track_version():
    """
    Track user version data for analytics purposes.
    Logs to feedback-version
    """
    helpers.check_allowed(True)
    # db.conn.feedback_version()
    # db.conn.log_statement('versions/add', json.dumps(request.args))
    return "", 200

@app.route('/playerInfo/get/') #BYPASS
def get_player_info(): #see formats/playerinfo_get.json
    """
    Get player participation statistics.
    All of this data is going to be a bitch to calculate, so for now I'm shortcutting it.
    This request failing to return data as expected is a major contributor to jointime slowdown.
    TODO actually do.
    """
    helpers.check_allowed(True)
    # session: sqlalchemy.orm.Session = Session()
    # player: Player = db.Player.from_ckey(request.args.get('ckey'), session)
    # if player is None: #Player doesn't exist, construct them before continuing.
    #     player = helpers.construct_player(session)
    #     session.add(player)
    # pass

    return jsonify({'participated': 0, 'seen': 0})

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
