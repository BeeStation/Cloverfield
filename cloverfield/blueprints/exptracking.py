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
    record: db.JobExperience = ply.jobexp.filter(db.JobExperience.key == request.args.get("type")).one_or_none()
    if(record is None):#Don't bother creating the record for now, we have more of these to handle.
        session.close()
        return jsonify({request.args.get('ckey'):{request.args.get('type'):0}})
    session.close()
    return jsonify({request.args.get('ckey'):{record.key:record.val}})
#FORMAT: ckey = Player.ckey, type = JobExperience.key, val = JobExperience.value
@api_exptrak.route('/clover/xptrak/set/')
def set_jobexp():
    check_allowed(True)
    ply: db.Player = db.Player.from_ckey(request.args.get("ckey"))
    record: db.JobExperience = ply.jobexp.filter(db.JobExperience.key == request.args.get("type")).one_or_none()
    if(record is None):
        record = db.JobExperience(
            request.args.get('ckey'),
            request.args.get('type'),
            request.args.get('val')
        )
        session.add(record)
    else:
        record.val = request.args.get('val')
    session.commit()
    return jsonify({"OK": "Experience Set."})
