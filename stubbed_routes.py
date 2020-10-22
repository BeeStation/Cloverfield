from flask import Blueprint, jsonify

api_deadroutes = Blueprint('unimplimented_routes', __name__)

#Gauntlet

@api_deadroutes.route('/gauntlet/getPrevious/')
def route_getgauntletdata():
    return jsonify({"error":"unimplimented"}) #I'm not sure this has EVER worked as a system.

#Stuff that probably isn't all that necessary and can stay dummied out like this.

@api_deadroutes.route('/map-switcher/switch/')
def route_mapswitch():
    return jsonify({"error":"unimplimented"}) #Not Currently Supported

@api_deadroutes.route('/bans/addException/')
def route_addbanimmunity():
    return jsonify({"error":"unimplimented"}) #This route SHOULD NEVER be actually implimented, it's stupid and dangerous.

@api_deadroutes.route('/bans/debug/')
def route_debugbans():
    return jsonify({"error":"unimplimented"}) #Debugging tool. Unnecessary for release.

#Bundle of routes: Ban Parity.

#This stuff seems to never be called, meaning I don't need to give a shit about them.

@api_deadroutes.route('/bans/updateRemote/')
def route_updateremotebans():
    return jsonify({"error":"unimplimented"}) #Part of the sync check, this is highly unlikely to ever occur in our setup, but it IS possible.

@api_deadroutes.route('/bans/updateLocal/')
def route_updatelocalbans():
    return jsonify({"error":"unimplimented"}) #Also unlikely.

@api_deadroutes.route('/bans/parity/')
def route_banparity():
    return jsonify({"error":"unimplimented"}) #Part of the above system.

#Antagonist Tracking
