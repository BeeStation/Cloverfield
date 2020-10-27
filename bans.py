import helpers
import neodb as db
from neodb import Session, Player, Ban, sessionmaker
from statics.database import FLAG_EXEMPT
import datetime
import sqlalchemy
import sqlalchemy.orm
import asyncio
from flask import Blueprint, request, jsonify, abort
from callback import hub_callback

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

    #Query CKEY bans directly so we can do matching.
    all_matching_bans.extend(list(session.query(db.Ban).filter(db.Ban.ckey == player.ckey).filter(db.Ban.removed == False)))

    #Retreive bans that match historic IP addresses.
    all_matching_bans.extend(list(session.query(db.Ban).filter(db.Ban.ip.in_(player.get_historic_inetaddr(session))).filter(db.Ban.removed == False)))

    #Likewise for CID
    all_matching_bans.extend(list(session.query(db.Ban).filter(db.Ban.cid.in_(player.get_historic_cid(session))).filter(db.Ban.removed == False)))

    #Deduplicate.
    all_matching_bans = list(dict.fromkeys(all_matching_bans))

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

@api_ban.route('/bans/add/')#Fucking CALLS BACK W H Y
def issue_ban(): #OH GOD TIMESTAMPS ARE BYOND ERA
    helpers.check_allowed(True)
    session: sqlalchemy.orm.Session = Session()
    new_ban = Ban(
        ckey =      request.args.get('ckey'),
        ip =        helpers.ip_getint(request.args.get('ip')) if request.args.get('ip') != 'N/A' else -1,
        cid =       request.args.get('compID') if request.args.get('compID') != 'N/A' else -1,
        akey =      request.args.get('akey'),
        oakey =     request.args.get('oakey'),
        reason =    request.args.get('reason'),
        timestamp = request.args.get('timestamp'),
        previous =  request.args.get('previous'),
        chain =     request.args.get('chain')
        )
    session.add(new_ban)
    session.flush() #Push to database.
    asyncio.run(hub_callback('addBan',{"ban":{
        "id":new_ban.id,
        "ckey":new_ban.ckey,
        "ip":helpers.ip_getstr(new_ban.ip) if new_ban.ip != -1 else 'N/A',
        "compID":new_ban.cid if new_ban.cid != -1 else 'N/A',
        "akey":new_ban.akey,
        "oakey":new_ban.oakey,
        "reason":new_ban.reason,
        "timestamp":new_ban.timestamp,
        "previous":new_ban.previous,
        "chain":new_ban.chain
    }}, secure=True))
    session.commit()
    return jsonify("OK")

@api_ban.route('/bans/delete/')
def remove_ban():
    helpers.check_allowed(True)
    session: sqlalchemy.orm.Session = Session()
    #Time to do some integrity checking.
    #All we *technically* need out of this request is an ID,
    #but to preserve security and make things a bit harder
    #to bruteforce, we're going to be exact about it and cross-check
    #every detail we can.

    #Retreive the assumedly targeted ban from the database.
    target_ban: db.Ban = db.Ban.from_id(session, request.args.get('id'))

    #Verify the data. If it's wrong close the session and abort.
    if  target_ban.ckey != request.args.get('ckey') or \
        target_ban.cid != request.args.get('compID') or \
        target_ban.ip != helpers.ip_getint(request.args.get('ip')):
        helpers.close_and_abort(session, 400)
    #Not finished tonight. TODO tomorrow.
    #Ban is correctly selected. Mark it deleted.
    target_ban.removed = True
    session.commit()
    return
