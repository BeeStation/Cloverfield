import helpers
import sqlalchemy
import neodb as db
import collections
from neodb import Session, Player
from flask import request, Blueprint, jsonify
from statics.database import RET_STR
api_extras = Blueprint('extras', __name__)

@api_extras.route('/playerInfo/getIPs/')
def get_player_ip_history():
    """
    Get the player's previous IP Addresses.
    """
    #This was actually extremely nice and clean.
    helpers.check_allowed(True)
    session: sqlalchemy.orm.Session = Session()
    #If a player gets passed to this and doesn't exist, just crash.
    player: Player = db.Player.from_ckey(request.args.get('ckey'), session)

    #TODO this code can probably be made a helper or deduped in some way
    #to be reused for the GetCIDs call.
    ip_list = player.get_historic_inetaddr(session, RET_STR)
    ctr = collections.Counter(ip_list)
    frequency_list = list()
    for entry in list(ctr):
        frequency_list.append({"ip":entry, "times":ctr[entry]})

    frequency_list.insert(0,{"last_seen":helpers.ip_getstr(player.last_ip)})
    return jsonify(frequency_list)

@api_extras.route('/versions/add/') #VOID
def track_version():
    """
    Track user version data for analytics purposes.
    Logs to feedback-version
    """
    helpers.check_allowed(True)
    # db.conn.feedback_version()
    # db.conn.log_statement('versions/add', json.dumps(request.args))
    return jsonify('OK')

@api_extras.route('/playerInfo/get/') #BYPASS
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
