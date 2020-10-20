import settings
import sqlalchemy
from flask import Flask, request, abort, jsonify
from orm_serializers import JSON_Goon


#Import prints.
import participation, secret_sauce, extras, bans

app = Flask(__name__)


#Register segmented modules.
app.register_blueprint(participation.api_participation)
app.register_blueprint(secret_sauce.api_secrets)
app.register_blueprint(extras.api_extras)
app.register_blueprint(bans.api_ban)

app.json_encoder = JSON_Goon #Overwrite the default encoder to serialize bans.


@app.route('/')
def hello_world():
    return 'BumbleGum API: API KEY IS ' + settings.API_KEY, 200

#Whatever crossed was doing last night.
if __name__ == '__main__':
    app.run()
