import helpers
import neodb as db
from neodb import Session, Player, Ban, sessionmaker
from statics.database import FLAG_EXEMPT
import datetime
import sqlalchemy
from flask import Blueprint, request, jsonify

api_ban = Blueprint('bans', __name__)

@api_ban.route('/bans/check/', methods = ['GET']) #BYPASS
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
    all_matching_bans: list = list()

    #We get this for free.
    all_matching_bans =+ player.bans.copy()

    #Update their previous data.
    if request.args.get('ip'):
        player.last_ip = helpers.ip_getint(request.args.get('ip'))
    if request.args.get('compID'):
        player.last_cid = request.args.get('compID')
    player.lastseen = datetime.datetime.utcnow()

    if len(all_matching_bans):
        all_matching_bans.insert(0, len(all_matching_bans)+1)
        session.commit()
        return jsonify(all_matching_bans) #This is so fucking stupid.
        #Returned format is fucking
        #[1,{ban},{ban}]... You have len() in byond. *just get the last entry in the fucking list*


    #Nothin' of note. Close her up.
    session.commit()
    return jsonify({'none': True})
