import cloverfield.db

from cloverfield.db import session, Player
from cloverfield.util.helpers import check_allowed, ip_getstr
from cloverfield.statics.database import *

import collections.abc
from flask import request, Blueprint, jsonify

api_extras = Blueprint('extras', __name__)

@api_extras.route('/playerInfo/getIPs/')
def get_player_ip_history():
    """
    Get the player's previous IP Addresses.
    """
    #This was actually extremely nice and clean.
    check_allowed(True)
    #If a player gets passed to this and doesn't exist, just crash.
    player: Player = db.Player.from_ckey(request.args.get('ckey'))

    #TODO this code can probably be made a helper or deduped in some way
    #to be reused for the GetCIDs call.
    ip_list = player.get_historic_inetaddr(RET_STR)
    ctr = collections.Counter(ip_list)
    frequency_list = list()
    for entry in list(ctr):
        frequency_list.append({"ip":entry, "times":ctr[entry]})

    frequency_list.insert(0,{"last_seen":ip_getstr(player.last_ip)})
    return jsonify(frequency_list)

@api_extras.route('/playerInfo/getCompIDs/')
def get_player_cid_history(): #God put me into this world to do terrible things. Like copypasting entire functions because I'm lazy.
    #This was actually extremely nice and clean.
    check_allowed(True)
    #If a player gets passed to this and doesn't exist, just crash.
    player: Player = db.Player.from_ckey(request.args.get('ckey'))

    #TODO #15 this code can probably be made a helper or deduped in some way
    #to be reused for the GetCIDs call.
    cid_list = player.get_historic_cid()
    ctr = collections.Counter(cid_list)
    frequency_list = list()
    for entry in list(ctr):
        frequency_list.append({"compID":str(entry), "times":ctr[entry]})

    frequency_list.insert(0,{"last_seen":str(player.last_cid)})
    return jsonify(frequency_list)

@api_extras.route('/versions/add/') #VOID
def track_version():
    """
    Track user version data for analytics purposes.
    Logs to feedback-version
    """
    check_allowed(True)
    # db.conn.feedback_version()
    # db.conn.log_statement('versions/add', json.dumps(request.args))
    return jsonify('OK')


