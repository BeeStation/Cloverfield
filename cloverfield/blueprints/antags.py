import cloverfield.db

from cloverfield.util.helpers import check_allowed
from cloverfield.db import Player, session

from flask import Blueprint, jsonify, request

api_antags = Blueprint('antagonist_history', __name__)

#I hate that this has to be here. -franc
#This doesn't have to be here tho -qwerty
antag_types = [
    'alien',
    'blob',
    'changeling',
    'conspirator',
    'gang_leader',
    'traitor',
    'grinch',
    'head_rev',
    'nukeop',
    'predator',
    'spy_thief',
    'vampire',
    'waldo',
    'werewolf',
    'wizard',
    'wraith',
    'wrestler'
]

@api_antags.route('/antags/history/')
def route_antaghistory_singlemode():
    check_allowed(True)
    #This route is gonna be pretty ugly.
    i = 0
    history: dict = dict()
    while request.args.get('players['+str(i)+']'):
        # history.append(get_antaghistory(request.args.get('ckeys['+str(i)+']'),request.args.get('role')))
        history[request.args.get('players['+str(i)+']')] = get_antaghistory(request.args.get('players['+str(i)+']'),request.args.get('role'), session)
        i += 1
    #Do additional transformations as necessary.

    return jsonify({"role":request.args.get('role'), "history":history})

def get_antaghistory(ckey, mode, session, calc:bool = False):
    """
    If `calc`, spend the extra cycles calculating their current percentage.
    """
    ply: db.Player = db.Player.from_ckey(ckey)
    rec_sen: db.Participation_Record = ply.participation.filter(db.Participation_Record.recordtype == ("participation_"+mode)).one_or_none()
    if rec_sen is None: #New player, go ahead and create the record at least.
        rec_sen = db.Participation_Record(
            ckey,
            ("participation_"+mode),
            0
        )
        session.add(rec_sen)
        session.commit()
    rec_cho: db.Participation_Record = ply.participation.filter(db.Participation_Record.recordtype == ("selected_"+mode)).one_or_none()
    if rec_cho is None:
        rec_cho = db.Participation_Record(
            ckey,
            ("selected_"+mode),
            0
        )
        session.add(rec_cho)
        session.commit()
    if calc:
        return {"seen": rec_sen.value, "selected": rec_cho.value, "percentage": (rec_cho.value/rec_sen.value if (rec_cho.value and rec_sen) else 0)}
    return {"seen": rec_sen.value, "selected": rec_cho.value}

@api_antags.route('/antags/record/')
def route_antaghistory_record(): #RECORDS /SELECTION/, not /PARTICIPATION/
    check_allowed(True)
    if request.args.get('assday'):
        return jsonify({"WOOP WOOP":"ASS. DAY.", "info":"Data discarded."})

    #Are we dealing with a batch or single request? This is the only API where they attempt to combine both and I despise it.
    if request.args.get('players[0][role]'):
        i = 0
        while request.args.get('players['+str(i)+'][role]'):
            ply: db.Player = db.Player.from_ckey(request.args.get('players['+str(i)+'][ckey]'))
            #IIRC, we should 100% have a selected entry at this point.
            rec: db.Participation_Record = ply.participation.filter(db.Participation_Record.recordtype == ("selected_"+request.args.get('players['+str(i)+'][role]'))).one_or_none()
            rec.value += 1
            i += 1
    else: #uuuugh this is ugly copypaste but I'm exhausted and I just want to see this working. FIXME FIXME FIXME
        ply: db.Player = db.Player.from_ckey(request.args.get('players'))
        #IIRC, we should 100% have a selected entry at this point.
        rec: db.Participation_Record = ply.participation.filter(db.Participation_Record.recordtype == ("selected_"+request.args.get('role'))).one_or_none()
        rec.value += 1
    session.commit()
    return jsonify({"OK":"Data Accepted"})

@api_antags.route('/antags/completeHistory/')
def route_antaghistory_full(): #god I already hate this and I haven't even started.
    return jsonify({"error":"[API] - This endpoint is unimplimented! Shout at Francinum!"})
