import hashlib
import settings
import helpers
import neodb as db
import sqlalchemy
from neodb import Session, Player, Ban, sessionmaker
from statics.database import FLAG_EXEMPT
import json
from flask import Flask, request, abort, jsonify
from orm_serializers import JSON_Goon
import datetime


#Import prints.
import participation, secret_sauce, extras

app = Flask(__name__)

#Register segmented modules.
app.register_blueprint(participation.api_participation)
app.register_blueprint(secret_sauce.api_secrets)
app.register_blueprint(extras.api_extras)

app.json_encoder = JSON_Goon #Overwrite the default encoder to serialize bans.


@app.route('/')
def hello_world():
    return 'BumbleGum API: API KEY IS ' + settings.API_KEY, 200


@app.route('/playerInfo/get/') #BYPASS
def get_player_info(): #see formats/playerinfo_get.json
    """
    Get player participation statistics.
    All of this data is going to be a bitch to calculate, so for now I'm shortcutting it.
    This request failing to return data as expected is a major contributor to jointime slowdown.
    TODO actually do.
    """
    helpers.check_allowed(True)
    # session: sqlalchemy.orm.Session = Session()
    # player: Player = db.Player.from_ckey(request.args.get('ckey'), session)
    # if player is None: #Player doesn't exist, construct them before continuing.
    #     player = helpers.construct_player(session)
    #     session.add(player)
    # pass

    return jsonify({'participated': 0, 'seen': 0})


#Whatever crossed was doing last night.
if __name__ == '__main__':
    # pylint: disable=undefined-variable
    APP.debug = True
    APP.run()
