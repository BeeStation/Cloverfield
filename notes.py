from flask import Blueprint, jsonify, request, abort
import settings
import helpers
import neodb as db
from neodb import Session
import sqlalchemy.orm


api_notes = Blueprint('notes', __name__)

@api_notes.route('/notes/', methods=['GET','POST'])
def handle_noteaccess():
    verify_notes()
    if request.args.get('action') == 'add':
        session: sqlalchemy.orm.Session = Session()
        note: db.PlayerNote = db.PlayerNote(
            request.args.get('server'),
            request.args.get('server_id'),
            request.args.get('ckey'),
            request.args.get('akey'),
            request.args.get('note')
        )
        session.add(note)
        session.commit()
        return jsonify({"OK":"Data Accepted"})
    if request.args.get('action') == 'delete':
        session: sqlalchemy.orm.Session = Session()
        note: db.PlayerNote = db.PlayerNote.from_id(session, request.args.get('id'))
        if note is None:
            helpers.close_and_abort(session, 400)
        note.deleted = True
        session.commit()
        return jsonify({"OK":"Note Marked Deleted."})
    if request.args.get('action') == 'get':
        #Okay, the return format for this is fucking stupid.
        #It expects the prefix of !!ID[note_id]
        #The rest is ENTIERELY UP TO US, AND SHOWS **RAW HTML TO THE ADMINISTRATOR**
        session: sqlalchemy.orm.Session = Session()
        ply: db.Player = db.Player.from_ckey(request.args.get('ckey'), session)
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
    if(request.args.get('auth') != settings.NOTES_KEY):
        abort(403)
