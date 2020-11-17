from cloverfield import db

from cloverfield.settings import *
from cloverfield.util.helpers import verify_api
from cloverfield.db import session

from flask import Blueprint, request, jsonify, abort


api_participation = Blueprint('participation', __name__)

@api_participation.route('/participation/record/')#VOID???
def record_individual_participation():
    """
    Record individual player participation.

    Relevant arguments:

    `ckey`, ckey

    `round_mode`, The gamemode currently being played.
    """
    #Okay. This may be how goon intends to define the start and end of a round.
    #...If it is I'm probably going to drink myself to death at the end of this.
    #Thankfully it's a void function so I can safely just neuter it for now.
    record_participation(request.args.get('ckey'),request.args.get('round_mode'))
    return jsonify('OK')

@api_participation.route('/participation/record-multiple/')#VOID???
def record_multi_participation():
    verify_api(request)
    #Same as above, but is passed multiple ckeys. In the future I'll probably make a DB func
    #and make this iteratively call it.
    #For now, I'm neutering these paths.
    if request.args.get('round_mode') is None or len(request.args) < 6:
        abort(400)
    i = 0
    while True:
        if record_participation(request.args.get('ckeys['+str(i)+']'), request.args.get('round_mode')):
            break
        i += 1
    return jsonify('OK')

def record_participation(ckey, mode):
    if ckey is None:
        return 1
    ply: db.Player = db.Player.from_ckey(ckey)
    basic_part: db.Participation_Record = ply.participation.filter(db.Participation_Record.recordtype == "participation_basic").one()
    basic_part.record()
    mode_str: str = "participation_"+mode
    mode_seen: db.Participation_Record = ply.participation.filter(db.Participation_Record.recordtype == mode_str).one_or_none()
    if mode_seen is None:
        mode_seen = db.Participation_Record.add(
            ckey,
            mode_str,
            0
        )
    mode_seen.record()
    return 0
