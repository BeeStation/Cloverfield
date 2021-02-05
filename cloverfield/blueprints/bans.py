from cloverfield import db

from cloverfield.db import session, Player, Ban
from cloverfield.settings import cfg
from cloverfield.statics.database import *
from cloverfield.proprietary import fetch_beebans
from cloverfield.util.topic import hub_callback
from cloverfield.util.helpers import check_allowed, ip_getint, ip_getstr

import datetime
import asyncio
from flask import Blueprint, request, jsonify, abort


api_ban = Blueprint('bans', __name__)

@api_ban.route('/bans/check/', methods = ['GET']) #BYPASS
def check_ban():
    check_allowed(True)
    #These are requested in a super weird format, *And are also our only form of connection log.*
    # ckey/compID/ip/record
    player: Player = db.Player.from_ckey(request.args.get('ckey'))
    if player is None: #Player doesn't exist, construct them before continuing.
        player = db.Player.add(request.args.get('ckey'), ip_getint(request.args.get('ip')), request.args.get('compID'))

    #Log Connection
    db.Connection.add(request.args.get('ckey'), ip_getint(request.args.get('ip')), request.args.get('compID'), request.args.get('record'), db.Round_Entry.get_latest(request.args.get('data_id')).id)

    #Generate Return
    if player.flags & FLAG_EXEMPT:#Exempt. We're done here.
        return jsonify({'exempt': True}) #NOTE: This stuff looks legacy. Is it still meant to be functional? -F

    #Do we care about bee bans?
    if cfg["check_beebans"]:
        #If they have a beeban, we don't need to care about checking clover-related bans.
        beebans: list = fetch_beebans(player.ckey)
        if beebans is not None:
            return jsonify(beebans)


    #Interrogate the ban table for the latest.
    all_matching_bans: list = list()

    #Query CKEY bans directly so we can do matching.
    all_matching_bans.extend(list(session.query(db.Ban).filter(db.Ban.ckey == player.ckey).filter(db.Ban.removed == False)))

    #Retreive bans that match historic IP addresses.
    all_matching_bans.extend(list(session.query(db.Ban).filter(db.Ban.ip.in_(player.get_historic_inetaddr())).filter(db.Ban.removed == False)))

    #Likewise for CID
    all_matching_bans.extend(list(session.query(db.Ban).filter(db.Ban.cid.in_(player.get_historic_cid())).filter(db.Ban.removed == False)))

    #Deduplicate.
    all_matching_bans = list(dict.fromkeys(all_matching_bans))

    #Update their previous data.
    if request.args.get('ip'):
        player.last_ip = ip_getint(request.args.get('ip'))
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
    check_allowed(True)
    new_ban = Ban.add(
        ckey =      request.args.get('ckey'),
        ip =        ip_getint(request.args.get('ip')) if request.args.get('ip') != 'N/A' else -1,
        cid =       request.args.get('compID') if request.args.get('compID') != 'N/A' else -1,
        akey =      request.args.get('akey'),
        oakey =     request.args.get('oakey'),
        reason =    request.args.get('reason'),
        timestamp = request.args.get('timestamp'),
        previous =  request.args.get('previous'),
        chain =     request.args.get('chain')
        )
    asyncio.run(hub_callback('addBan',{"ban":{
        "id":new_ban.id,
        "ckey":new_ban.ckey,
        "ip":ip_getstr(new_ban.ip) if new_ban.ip != -1 else 'N/A',
        "compID":new_ban.cid if new_ban.cid != -1 else 'N/A',
        "akey":new_ban.akey,
        "oakey":new_ban.oakey,
        "reason":new_ban.reason,
        "timestamp":new_ban.timestamp,
        "previous":new_ban.previous,
        "chain":new_ban.chain
    }}, secure=True))
    return jsonify("OK")

@api_ban.route('/bans/delete/')
def remove_ban():
    check_allowed(True)
    #Time to do some integrity checking.
    #All we *technically* need out of this request is an ID,
    #but to preserve security and make things a bit harder
    #to bruteforce, we're going to be exact about it and cross-check
    #every detail we can.

    #Retreive the assumedly targeted ban from the database.
    target_ban: db.Ban = db.Ban.from_id( request.args.get('id'))

    #Verify the data. If it's wrong close the session and abort.
    try:
        if  target_ban.ckey != request.args.get('ckey') or \
            target_ban.cid != int(request.args.get('compID')) or \
            target_ban.ip != int(ip_getint(request.args.get('ip'))):
            abort(400)
    except Exception:
        abort(400)
        #This is probably still vulnerable to some kinda timing attck but who cares it's spacebans.
    #Not finished tonight. TODO tomorrow.
    #Ban is correctly selected. Mark it deleted.
    target_ban.remove()
    asyncio.run(hub_callback('deleteBan',{"ban":{
        "id":target_ban.id,
        "ckey":target_ban.ckey,
        "ip":ip_getstr(target_ban.ip) if target_ban.ip != -1 else 'N/A',
        "compID":target_ban.cid if target_ban.cid != -1 else 'N/A',
        "akey":str(request.args.get('akey')),
        "oakey":target_ban.oakey,
        "reason":target_ban.reason,
        "timestamp":target_ban.timestamp,
        "previous":target_ban.previous,
        "chain":target_ban.chain
    }}, secure=True))
    return jsonify("OK")

@api_ban.route('/bans/edit/')
def edit_ban():
    check_allowed(True)
    target_ban: db.Ban = db.Ban.from_id( request.args.get('id'))
    if target_ban is not None:
        target_ban.ckey =      request.args.get('ckey')
        target_ban.ip =        ip_getint(request.args.get('ip')) if request.args.get('ip') != 'N/A' else -1
        target_ban.cid =       request.args.get('compID') if request.args.get('compID') != 'N/A' else -1
        target_ban.akey =      request.args.get('akey')
        target_ban.reason =    request.args.get('reason')
        target_ban.timestamp = request.args.get('timestamp')
        session.flush()
        asyncio.run(hub_callback('editBan',{"ban":{
            "id":target_ban.id,
            "ckey":target_ban.ckey,
            "ip":target_ban.ip_getstr(target_ban.ip) if target_ban.ip != -1 else 'N/A',
            "compID":target_ban.cid if target_ban.cid != -1 else 'N/A',
            "akey":target_ban.akey,
            "oakey":target_ban.oakey,
            "reason":target_ban.reason,
            "timestamp":target_ban.timestamp,
            "previous":target_ban.previous,
            "chain":target_ban.chain
        }}, secure=True))
        return jsonify("OK")
    else:
        asyncio.run(hub_callback('editBan',{"Ban does not exist."}))
        return jsonify("OK")
    return {"ERROR"}

# Jobban retrieval route
# Expected Return Structure: {"ckey":["Bantype","Bantype","Bantype"]}
# Arguments: ckey, removed (Include removed bans. Not currently implimented.)
@api_ban.route('/jobbans/get/player/')
def get_plyjobban():
    check_allowed(True)
    if request.args.get('ckey') is None:
        abort(400)
    ply: Player = Player.from_ckey(request.args.get('ckey'))
    if ply is None: #Can't ban the nonexistant.
        return jsonify({request.args.get('ckey'):[]})
    banlist: list = ply.jobbans.filter(db.JobBan.removed == 0).all()
    xlist = list()
    x: db.JobBan
    for x in banlist:
        xlist.append(x.rank)
    return jsonify({request.args.get('ckey'):xlist})

#args removed (Unimplimented.)
@api_ban.route('/jobbans/get/all/')
def get_alljobban():
    check_allowed(True)
    allbans:list = list(session.query(db.JobBan).filter(db.JobBan.removed == 0).all())
    ret:dict = dict()
    x: db.JobBan
    for x in allbans:
        if x.ckey in ret:
            ret[x.ckey].append(x.rank)
        else:
            ret[x.ckey]:list = list([x.rank])
    return jsonify(ret)

# Arguments: ckey, rank
@api_ban.route('/jobbans/del/')
def rem_jobban():
    check_allowed(True)
    if request.args.get('ckey') is None or request.args.get('rank') is None:
        abort(400)
    ply: Player = Player.from_ckey(request.args.get('ckey'))
    ban: db.JobBan = ply.jobbans.filter(db.JobBan.removed == 0).filter(db.JobBan.rank == request.args.get('rank')).one_or_none()
    if ban is None:
        jsonify({"Error":"Ban does not exist or is already removed."})
    ban.remove()
    return jsonify({"OK":"Ban Removed."})

@api_ban.route('/jobbans/add/')
def add_jobban():
    check_allowed(True)
    if request.args.get('ckey') is None or request.args.get('rank') is None or request.args.get('akey') is None:
        abort(400)
    ban = db.JobBan.add(
        request.args.get('ckey'),
        request.args.get('rank'),
        request.args.get('akey'),
        request.args.get('applicable_server') if request.args.get('applicable_server') != "" else None
    )
    return jsonify({"OK":"Ban Issued."})
