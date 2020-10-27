from flask import request, Blueprint, abort, jsonify
import jwt
import datetime
import settings
import neodb as db
import sqlalchemy.orm
from neodb import Session
import re
import flask.json
import helpers
from round_tracking import latest_known_rounds
api_secure = Blueprint('secure', __name__)

#Isolation file for the ban panel.
#This route *MUST* be secure, as it's public facing.

#Failure to keep this route secure and resistant to attack would result in the ability for an attacker to dump the contents of the ban database.
#Including removed bans, with full details.

#Request structure


#Basic Get

    #Security terms

        #t      = Insecure random float, 0-<1.
        #auth   = API key, MD5 hashed.
        #tok    = Authenticated JWT issued to the client by the server.

    #Functionary terms
        #search['+column+'] = term
        #sort               = sort
        #order              = order
        #offset             = offset
        #limit              = limit
        #removed            = removed

        #Additional datapoints for serve


#Auth route, see formats/ultrasec.txt
@api_secure.route('/usec/auth/get/')
def usec_issuejwt():
    if int(request.args.get('data_version')) != settings.API_REV:
        abort(400)
    pl = {
        #Qualified Claims
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2),
        'nbf': datetime.datetime.utcnow(),
        'iss': 'Cloverfield',
        'aud': 'CF_BANLIST',
        'iat': datetime.datetime.utcnow(),

        #Private Use Claims
        'rid': latest_known_rounds[request.args.get('servertag')],  #Lock tokens to individual rounds.
        'adm': request.args.get('administrator'),                   #Auditing.
        'arv': settings.API_REV
    }
    b_token = jwt.encode(pl,settings.US_SECRET,algorithm='HS512')
    str_token = b_token.decode('utf-8')
    return jsonify({"token":str_token})

#FIXME DISABLE IN PRODUCTION.
@api_secure.route('/usec/auth/test/')
def usec_testjwt():
    verify_secure()
    return jsonify({"OK": "Token is VALID."})


#Ban Retrieval API
@api_secure.route('/usec/bans/get')
def secure_get_banpanel():
    z = verify_secure()
    if z is not None:
        return z, 401
    rsp:flask.Response
    if request.args.get('search[all]') is not None:
        rsp = jsonify(bans_sort_all())
    if request.args.get('search[akey]') is not None:
        rsp = jsonify(bans_sort_akey())
    if request.args.get('search[ckey]') is not None:
        rsp = jsonify(bans_sort_ckey())
    if request.args.get('search[reason]') is not None:
        rsp = jsonify(bans_sort_reason())
    if request.args.get('search[compID]') is not None:
        rsp = jsonify(bans_sort_compID())
    if request.args.get('search[ip]') is not None:
        rsp = jsonify(bans_sort_ip())
    if rsp is None:
        rsp = jsonify({'ERROR':'Unimplimented'})
    rsp.headers.add("Access-Control-Allow-Origin", "*")
    return rsp

#Please join me in hell as I copypaste all this shit.

def bans_sort_all():
    session:sqlalchemy.orm.Session = Session()
    searchval:str = str(request.args.get('search[all]'))
    if searchval == '' or None:
        searchval = '%'
    query: sqlalchemy.orm.query = session.query(db.Ban).filter(db.Ban.removed == int(request.args.get('removed')))\
        .filter(sqlalchemy.or_(
            db.Ban.ckey.like(searchval),
            db.Ban.akey.like(searchval),
            db.Ban.reason.like(searchval),
            db.Ban.ip.like(helpers.ip_getint(searchval)),
            db.Ban.cid.like(searchval),
            db.Ban.oakey.like(searchval)
        ))
    ret = dict()
    bans: list = query.limit(int(request.args.get('limit'))).all()
    x:db.Ban
    for x in bans:
        ret.update({str(x.id): flask.json.loads(flask.json.dumps(x))})
    ret.update({'total': query.count()})
    session.close()
    return ret

def bans_sort_ckey():
    session:sqlalchemy.orm.Session = Session()
    searchval:str = str(request.args.get('search[ckey]'))
    if searchval == '' or None:
        searchval = '%'
    query: sqlalchemy.orm.query = session.query(db.Ban).filter(db.Ban.removed == int(request.args.get('removed')))\
        .filter(sqlalchemy.or_(
            db.Ban.ckey.like(searchval)
        ))
    ret = dict()
    bans: list = query.limit(int(request.args.get('limit'))).all()
    x:db.Ban
    for x in bans:
        ret.update({str(x.id): flask.json.loads(flask.json.dumps(x))})
    ret.update({'total': query.count()})
    session.close()
    return ret

def bans_sort_akey():
    session:sqlalchemy.orm.Session = Session()
    searchval:str = str(request.args.get('search[akey]'))
    if searchval == '' or None:
        searchval = '%'
    query: sqlalchemy.orm.query = session.query(db.Ban).filter(db.Ban.removed == int(request.args.get('removed')))\
        .filter(sqlalchemy.or_(
            db.Ban.akey.like(searchval),
            db.Ban.oakey.like(searchval)
        ))
    ret = dict()
    bans: list = query.limit(int(request.args.get('limit'))).all()
    x:db.Ban
    for x in bans:
        ret.update({str(x.id): flask.json.loads(flask.json.dumps(x))})
    ret.update({'total': query.count()})
    session.close()
    return ret

def bans_sort_reason():
    session:sqlalchemy.orm.Session = Session()
    searchval:str = str(request.args.get('search[reason]'))
    if searchval == '' or None:
        searchval = '%'
    query: sqlalchemy.orm.query = session.query(db.Ban).filter(db.Ban.removed == int(request.args.get('removed')))\
        .filter(sqlalchemy.or_(
            db.Ban.reason.like(searchval)
        ))
    ret = dict()
    bans: list = query.limit(int(request.args.get('limit'))).all()
    x:db.Ban
    for x in bans:
        ret.update({str(x.id): flask.json.loads(flask.json.dumps(x))})
    ret.update({'total': query.count()})
    session.close()
    return ret

def bans_sort_compID():
    session:sqlalchemy.orm.Session = Session()
    searchval:str = str(request.args.get('search[compID]'))
    if searchval == '' or None:
        searchval = '%'
    query: sqlalchemy.orm.query = session.query(db.Ban).filter(db.Ban.removed == int(request.args.get('removed')))\
        .filter(sqlalchemy.or_(
            db.Ban.cid.like(searchval)
        ))
    ret = dict()
    bans: list = query.limit(int(request.args.get('limit'))).all()
    x:db.Ban
    for x in bans:
        ret.update({str(x.id): flask.json.loads(flask.json.dumps(x))})
    ret.update({'total': query.count()})
    session.close()
    return ret

def bans_sort_ip():
    session:sqlalchemy.orm.Session = Session()
    searchval:str = str(request.args.get('search[ip]'))
    if searchval == '' or None:
        searchval = '%'
    query: sqlalchemy.orm.query = session.query(db.Ban).filter(db.Ban.removed == int(request.args.get('removed')))\
        .filter(sqlalchemy.or_(
            db.Ban.ip.like(helpers.ip_getint(searchval))
        ))
    ret = dict()
    bans: list = query.limit(int(request.args.get('limit'))).all()
    x:db.Ban
    for x in bans:
        ret.update({str(x.id): flask.json.loads(flask.json.dumps(x))})
    ret.update({'total': query.count()})
    session.close()
    return ret

#Another annoyingly specific route. Stub and investigate later.
@api_secure.route('/usec/bans/getPrevious')
def secure_getprevious_banpanel():
    verify_secure()
    return 200

#Considerations for security:
#Verify JWT to the round and expiry time, If the expiry window has passed
# notify them to reopen the panel, as they've somehow managed to use
# the ban panel for greater than two hours. As we are signing and
# issuing them ourselves, we don't need to worry about clock jitter.

def verify_secure():
    try:
        x:dict=jwt.decode(bytes(request.args.get('token') if request.args.get('token') is not None else request.args.get('auth'), 'utf8'), settings.US_SECRET, algorithms='HS512', audience='CF_BANLIST')
        #FIXME CHECK DISABLED FOR TESTING, DO NOT RUN IN PROD.
        # if int(x['rid']) != latest_known_rounds[request.args.get('servertag') if request.args.get('servertag') is not None else request.args.get('data_id')]: #Token expired by round change.
        #     raise Exception("Token expired by round ID mismatch.")
        if int(x['arv']) != settings.API_REV:
            raise Exception("!!!TOKEN CLAIMS VALID BUT API VERSION IS WRONG!!!") #This should never happen.
    except: #trap every single error and forbid.
        return {"error":"Token invalid, it may be expired."}
    return

#Probably
