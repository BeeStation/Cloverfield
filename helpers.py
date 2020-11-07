import settings
import ipaddress
from flask import request, abort
import neodb as db
import sqlalchemy, sqlalchemy.orm
import collections

#Reusables, primarily key authentication
def verify_api(packet):
    """
    Verify request API token is valid.
    """
    auth = packet.args.get('auth')
    if(not auth):
        abort(401)
    if(auth == settings.API_KEY):
        return
    return abort(403)


def check_allowed(check_key=False, api_version=settings.API_REV):
    """
    Configurable integrity check function.

    `packet` is the active request object.

    `check_key` (Default `False`), Verify API access is allowed.

    `api_version` (Default `API_REV`), Current allowed API verson.
    """
    if(int(request.args.get('data_version')) != api_version):
        abort(400)
    if(check_key):
        verify_api(request)

def ip_getint(ip):
    """
    Get Int version of IP
    """
    try:
        return int(ipaddress.IPv4Address(ip))
    except:
        return 0

def ip_getstr(ip):
    """
    Get string version of IP
    """
    try:
        return str(ipaddress.IPv4Address(ip))
    except:
        return 0

def log_connection(session: sqlalchemy.orm.Session):
    """
    Log the connection to the `connection` table. The backbone of ban checking.

    Utilizes global `request` object, must be provided with a `session`

    Also handles round seen tracking.
    """

    session.begin_nested()
    conlog = db.Connection(
        request.args.get('ckey'),
        ip_getint(request.args.get('ip')),
        request.args.get('compID'),
        request.args.get('record'),
        db.Round_Entry.get_latest(session, request.args.get('data_id')).id,
    )
    session.add(conlog)
    if bool(request.args.get('record')) is True:#First connection this round, track the fact that they have at least seen it.
        rec_sen: db.Participation_Record = session.query(db.Participation_Record).filter(db.Participation_Record.ckey == request.args.get('ckey')).filter(db.Participation_Record.recordtype == "seen_basic").one_or_none()
        if rec_sen is None: #New player, Fill in the part of their record we care about right now.
            rec_sen = db.Participation_Record(
                request.args.get('ckey'),
                "seen_basic",
                0)
            session.add(rec_sen)
        rec_sen.value += 1
    session.commit()

def construct_player(session: sqlalchemy.orm.Session):
    """
    Construct a new entry to `player`, Must have `request` context.

    DOES NOT ADD IT TO THE SESSION.
    """
    session.begin_nested()
    ply = db.Player(
        request.args.get('ckey'),
        ip_getint(request.args.get('ip')),
        request.args.get('compID')
    )
    session.add(ply)
    session.commit()
    return ply

def close_and_abort(session: sqlalchemy.orm.Session, code):
    session.close()
    abort(code)
