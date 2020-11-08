from cloverfield import db

from cloverfield.settings import *
from cloverfield.util.helpers import check_allowed, ip_getstr
from cloverfield.db import Connection, Round_Entry, session, Player, Participation_Record

from flask import Blueprint, jsonify, abort, request
import datetime

api_rounds = Blueprint('rounds', __name__)
latest_known_rounds: dict = dict() #{server_key:round_id}, {main:1}, used to invalidate JWTs



@api_rounds.route('/roundstate', methods=['GET','POST'])
def handle_roundstate():
    verify_parser()
    #Switch by round_status argument
    if(request.args.get('round_status') == 'start'):
        old_rnd: Round_Entry = Round_Entry.get_latest(session, request.args.get('round_server'))
        if old_rnd is not None and old_rnd.reason is None:  #The round was restarted without providing a reason.
            old_rnd.reason = 3      #Fill in reason column to prevent repeat and to mark rounds as errored.
        #We need to create the round datum.
        rnd = Round_Entry.add(
            request.args.get('round_server'),
            request.args.get('round_server_number'),
            request.args.get('round_name'),
            datetime.datetime.utcnow()
        )
        session.commit()
        return jsonify("OK")

    if(request.args.get('round_status') == 'end'):
        rnd: Round_Entry = Round_Entry.get_latest(session, request.args.get('round_server'))
        rnd.end_name = request.args.get('round_name')
        rnd.mode = request.args.get('mode')
        rnd.reason = request.args.get('end_reason')
        rnd.end_stamp = datetime.datetime.utcnow()
        session.commit()
        return jsonify("OK")
    session.close()
    return abort(400)



@api_rounds.route('/playerInfo/get/') #BYPASS
def get_player_info(): #see formats/playerinfo_get.json
    """
    Get player participation statistics.
    All of this data is going to be a bitch to calculate, so for now I'm shortcutting it.
    This request failing to return data as expected is a major contributor to jointime slowdown.
    TODO actually do.
    """
    check_allowed(True)
    #Okay. This proc expects there to be a difference between these values.
    #The thing is, tracking one of these values over the other is a lot more difficult than you'd think.
    #So for now, I'm going to tie both of them to the same value.
    #Actually, it's surprisingly fine. I just need to be careful about things.
    ply: Player = Player.from_ckey(request.args.get('ckey'))
    #Turns out this route fires before bans are checked.
    if ply is None:
        return jsonify({'participated': 0, 'seen': 0})
    rec_par: Participation_Record = ply.participation.filter(Participation_Record.recordtype == "participation_basic").one_or_none()
    if rec_par is None: #New player, Fill in their record.
        rec_par = Participation_Record.add(
            request.args.get('ckey'),
            "participation_basic",
            0
        )
    rec_sen: Participation_Record = ply.participation.filter(Participation_Record.recordtype == "seen_basic").one_or_none()
    if rec_sen is None: #New player, Fill in their record.
        rec_sen = Participation_Record.add(
            request.args.get('ckey'),
            "seen_basic",
            0
        )
    session.commit()
    return jsonify({'participated': rec_par.value, 'seen': rec_sen.value, 'last_ip': ip_getstr(ply.last_ip), 'last_compID': str(ply.last_cid)})

def verify_parser():
    if(request.args.get('token') is None):
        abort(401)
    if(request.args.get('token') != HUBLOG_KEY):
        abort(403)
    return 0
