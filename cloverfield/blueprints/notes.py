from cloverfield import db

from cloverfield.settings import *
from cloverfield.db import session

from flask import Blueprint, jsonify, request, abort

api_notes = Blueprint('notes', __name__)

@api_notes.route('/notes/', methods=['GET','POST'])
def handle_noteaccess():
    verify_notes()
    if request.args.get('action') == 'add':
        note: db.PlayerNote = db.PlayerNote.add(
            request.args.get('server'),
            request.args.get('server_id'),
            request.args.get('ckey'),
            request.args.get('akey'),
            request.args.get('note')
        )
        session.commit()
        return jsonify({"OK":"Data Accepted"})
    if request.args.get('action') == 'delete':
        note: db.PlayerNote = db.PlayerNote.from_id(session, request.args.get('id'))
        if note is None:
            abort(400)
        note.deleted = True
        session.commit()
        return jsonify({"OK":"Note Marked Deleted."})
    if request.args.get('action') == 'get':
        #Okay, the return format for this is fucking stupid.
        #It expects the prefix of !!ID[note_id]
        #The rest is ENTIERELY UP TO US, AND SHOWS **RAW HTML TO THE ADMINISTRATOR**
        ply: db.Player = db.Player.from_ckey(request.args.get('ckey'))
        if ply is None:
            return 'Player has no database entry.', 200
        bigass_bundle: str = str()
        x: db.PlayerNote
        for x in ply.notes:
            if x.deleted:
                continue
            bigass_bundle += "!!ID"+str(x.id)+"</a><b>ID:"+str(x.id)+"|ADMIN:"+x.akey+"|SERVER:"+x.server_id+"</b>\n"+x.note+"<hr>"
        if len(bigass_bundle) < 3:
            bigass_bundle = 'No Notes.'
        return bigass_bundle, 200
    abort(400)

def verify_notes():
    if(request.args.get('auth') is None):
        abort(401)
    if(request.args.get('auth') != NOTES_KEY):
        abort(403)
