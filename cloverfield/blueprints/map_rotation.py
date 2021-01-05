from flask import Blueprint, jsonify
from cloverfield.util import interact_tgs
from cloverfield.util.helpers import check_allowed
from cloverfield.settings import cfg

api_maprotation = Blueprint('map_rotation', __name__)


@api_maprotation.route('/map-switcher/switch/')
def route_mapswitch():
    check_allowed(True)
    if(cfg["tgs"]["host"] == "invalid.org"):
        #TGS Not configured, Abort.
        return jsonify({"error":"This API Does not support Mapswitching. Contact your host."}), 500
    interact_tgs.trigger_compile()
    return jsonify({"response":"201"}), 200 # this format is weird because it's forwarding jenkins shit.
