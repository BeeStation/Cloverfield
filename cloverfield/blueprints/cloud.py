from cloverfield import db

from cloverfield.settings import cfg
from cloverfield.db import session, Player, CloudSave, CloudData

import urllib.parse
from flask import Blueprint, request, abort, jsonify

api_cloudhub = Blueprint('cloud', __name__)

# Cloud Route
# The absolute most monolithic and awful route of the entire system.
# Controlled entirely by parameters and stored in a godawful, confusing format.
# I'm likely going to end up blindly accepting whatever is sent and push it to the backend without question.

# Y'see all the bitching I did above?
# Yeah no. This system is actually quite clean for what it could be.

@api_cloudhub.route('/cloudsaves', methods=['POST','GET'])
def cloud_hell():
    verify_cloud()
    route:str = list(request.args)[0]
    player: Player = Player.from_ckey(request.args.get('ckey'))
    if route == 'list':#Sure, fuck it, take everything.
        saves = dict()
        data = dict()

        x: db.CloudSave
        for x in player.saves:
            saves.update({x.save_name:x.save})
        x: db.CloudData
        for x in player.data:
            data.update({x.key:x.value})
        return jsonify({"saves":saves,"cdata":data})
    if route == 'put': #Okay shit we actually have to store things.
        sav: CloudSave = CloudSave.add(
            player.ckey,
            request.args.get('name'),
            request.args.get('data')
        )
        return jsonify({"status":"OK"})
    if route == 'delete': #Find the cloud save by name and delete it.
        sav: CloudSave = session.query(CloudSave).filter(CloudSave.ckey == player.ckey).filter(CloudSave.save_name == request.args.get('name')).one_or_none()
        if sav is None:
            abort(400) #What the fuck do you want us to delete asshole?
        session.delete(sav)
        session.commit()
        return jsonify({"status":"OK"})
    if route == 'dataput': #Abitrary, key-based write and update-only data storage. This one might get unpleasant.
        dat: CloudData = session.query(CloudData).filter(CloudData.ckey == player.ckey).filter(CloudData.key == request.args.get('key')).one_or_none()
        if dat is not None:
            dat.update(urllib.parse.unquote(request.args.get('value')))
            return jsonify({"status":"OK"})
        dat = CloudData.add(
            player.ckey,
            request.args.get('key'),
            urllib.parse.unquote(request.args.get('value'))
        )
        return jsonify({"status":"OK"})
    if route == 'get': #Okay why does it fucking call this they got them the first time wtf
        sav: CloudSave = session.query(CloudSave).filter(CloudSave.ckey == player.ckey).filter(CloudSave.save_name == request.args.get('name')).one_or_none()
        if sav is None:
            abort(400) #What the fuck do you want us to get asshole?
        return jsonify({"savedata":sav.save})
    return jsonify({"status":"error","error":"Invalid Route. Contact Francinum."})

def dump_user_data():
    pass


def verify_cloud(): #The cloud has it's own auth system. I hate it.
    if(request.args.get('api_key') is None):
        abort(401)
    if(request.args.get('api_key') != cfg["keys"]["cloud_key"]):
        abort(403)
    return 0
