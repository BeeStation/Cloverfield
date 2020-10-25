import settings
import sqlalchemy
from flask import Flask, request, abort, jsonify
from orm_serializers import JSON_Goon


#Import prints.
import participation, secret_sauce, extras, bans, cloud, stubbed_routes, round_tracking, antags, secure, notes, exptracking

app = Flask(__name__)


#Register segmented modules.
app.register_blueprint(participation.api_participation) #COMPLETE, mercifully
app.register_blueprint(secret_sauce.api_secrets)        #COMPLETE
app.register_blueprint(extras.api_extras)               #Versions/add isn't necessary to release.
app.register_blueprint(bans.api_ban)                    #COMPLETE (See secure.py for the ban panel getter)
app.register_blueprint(cloud.api_cloudhub)              #COMPLETE
app.register_blueprint(stubbed_routes.api_deadroutes)   #Explicitly unfinished.
app.register_blueprint(round_tracking.api_rounds)
app.register_blueprint(antags.api_antags)
app.register_blueprint(secure.api_secure)
app.register_blueprint(notes.api_notes)
app.register_blueprint(exptracking.api_exptrak)

app.json_encoder = JSON_Goon #Overwrite the default encoder to serialize bans.

#Whatever crossed was doing last night.
if __name__ == '__main__':
    app.run()
