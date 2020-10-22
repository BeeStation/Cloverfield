import settings
import sqlalchemy
from flask import Flask, request, abort, jsonify
from orm_serializers import JSON_Goon


#Import prints.
import participation, secret_sauce, extras, bans, cloud, stubbed_routes, round_tracking, antags

app = Flask(__name__)


#Register segmented modules.
app.register_blueprint(participation.api_participation) #Not even started.
app.register_blueprint(secret_sauce.api_secrets)        #COMPLETE
app.register_blueprint(extras.api_extras)               #Needs Playerinfo populated.
app.register_blueprint(bans.api_ban)                    #Needs unban.
app.register_blueprint(cloud.api_cloudhub)              #COMPLETE
app.register_blueprint(stubbed_routes.api_deadroutes)   #Explicitly unfinished.
app.register_blueprint(round_tracking.api_rounds)
app.register_blueprint(antags.api_antags)

app.json_encoder = JSON_Goon #Overwrite the default encoder to serialize bans.

#Whatever crossed was doing last night.
if __name__ == '__main__':
    app.run()
