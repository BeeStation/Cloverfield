from flask import Blueprint, request, jsonify, abort
import sqlalchemy.orm
import settings
import helpers
import neodb as db
from neodb import Session

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
    session = Session()
    record_participation(request.args.get('ckey'),request.args.get('round_mode'), session)
    session.commit()
    return jsonify('OK')

@api_participation.route('/participation/record-multiple/')#VOID???
def record_multi_participation():
    helpers.verify_api(request)
    #Same as above, but is passed multiple ckeys. In the future I'll probably make a DB func
    #and make this iteratively call it.
    #For now, I'm neutering these paths.
    if request.args.get('round_mode') is None or len(request.args) < 6:
        abort(400)
    session = Session()
    i = 0
    while True:
        if record_participation(request.args.get('ckeys['+str(i)+']'), request.args.get('round_mode'), session):
            break
        i += 1
    session.commit()
    return jsonify('OK')

def record_participation(ckey, mode, session: sqlalchemy.orm.Session):
    if ckey is None:
        return 1
    ply: db.Player = db.Player.from_ckey(ckey, session)
    basic_part: db.Participation_Record = ply.participation.filter(db.Participation_Record.recordtype == "participation_basic").one()
    basic_part.value += 1
    mode_str: str = "participation_"+mode
    mode_seen: db.Participation_Record = ply.participation.filter(db.Participation_Record.recordtype == mode_str).one_or_none()
    if mode_seen is None:
        mode_seen = db.Participation_Record(
            ckey,
            mode_str,
            0
        )
        session.add(mode_seen)
    mode_seen.value += 1
    session.commit()
    return 0