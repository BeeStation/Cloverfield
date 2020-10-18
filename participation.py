from flask import Blueprint, request, jsonify

api_participation = Blueprint('participation', __name__)

@api_participation.route('/participation/record/')#VOID???
def record_individual_participation():
    """
    Record individual player participation.

    Relevant arguments:

    `ckey`, ckey

    `round_mode`, The gamemode currently being played.
    """
    #Okay. This may be how goon intends to define the start and end of a round.
    #...If it is I'm probably going to drink myself to death at the end of this.
    #Thankfully it's a void function so I can safely just neuter it for now.
    return jsonify('OK')

@api_participation.route('/participation/record-multiple/')#VOID???
def record_multi_participation():
    #Same as above, but is passed multiple ckeys. In the future I'll probably make a DB func
    #and make this iteratively call it.
    #For now, I'm neutering these paths.
    return jsonify('OK')
