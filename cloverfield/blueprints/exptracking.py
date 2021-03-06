from cloverfield import db

from cloverfield.util.helpers import check_allowed
from cloverfield.db import session

from flask import request, Blueprint, abort, jsonify
#Cloverfield specific routes to replace the BYOND hub in the business of job experience tracking.

api_exptrak = Blueprint('exp_tracking', __name__)


#FORMAT: ckey = Player.ckey, type = JobExperience.key
@api_exptrak.route('/clover/xptrak/get/')
def get_jobexp():
    check_allowed(True)
    ply: db.Player = db.Player.from_ckey(request.args.get("ckey"))
    if ply:
        record: db.JobExperience = ply.jobexp.filter(db.JobExperience.key == request.args.get("type")).one_or_none()
        if record:
            return jsonify({request.args.get('ckey'):{record.key:record.val}})
    #Don't bother creating the record for now, and if they somehow don't have a player, sucks. we have more of these to handle.
    return jsonify({request.args.get('ckey'):{request.args.get('type'):0}})

#FORMAT: ckey = Player.ckey, type = JobExperience.key, val = JobExperience.value
@api_exptrak.route('/clover/xptrak/set/')
def set_jobexp():
    check_allowed(True)
    ply: db.Player = db.Player.from_ckey(request.args.get("ckey"))
    record: db.JobExperience = ply.jobexp.filter(db.JobExperience.key == request.args.get("type")).one_or_none()
    if(record is None):
        record = db.JobExperience.add(
            request.args.get('ckey'),
            request.args.get('type'),
            request.args.get('val')
        )
    else:
        record.val = request.args.get('val')
    return jsonify({"OK": "Experience Set."})
