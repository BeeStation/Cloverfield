from flask import Blueprint, jsonify

from cloverfield.util.helpers import check_allowed
from cloverfield.settings import cfg

vpn_detection = Blueprint('vpn_detection', __name__)

@vpn_detection.route('/vpncheck')
def vpn_processor():
    check_allowed(True)
    jsonify({"message":"API route incomplete. Complain to Francinum."})

@vpn_detection.route("/vpncheck-whitelist/<string:mode>")
def vpn_whitelist(mode: str): #modes supported: `add` `remove`
    check_allowed(True)
    jsonify({"message":"API route incomplete. Complain to Francinum."}), 501
