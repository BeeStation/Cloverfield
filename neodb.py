import settings
import helpers
import sqlalchemy
from sqlalchemy import * # pylint: disable=unused-wildcard-import
from urllib.parse import quote
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, Session
from sqlalchemy.orm.exc import NoResultFound
from statics.database import * # pylint: disable=unused-wildcard-import
import datetime
import collections

FLAG_EXEMPT =   1<<1    #Exempt from bans. This is probably legacy but I'm supporting it anyways.


Session = sessionmaker()
Session.configure(bind = create_engine((
    'mysql://'+
    quote(settings.MARIADB_USER)+':'+quote(settings.MARIADB_PASS)+
    '@'+quote(settings.MARIADB_SERVER)+':'+quote(str(settings.MARIADB_PORT))+'/'+quote(settings.MARIADB_DBNAME)
    )))

decbase = declarative_base()

#Thank tapdancing christ that these are the only structs the central API cares about.

class Player(decbase):
    __tablename__ = 'players'

    id =        Column('id',        Integer(),primary_key=True)
    ckey =      Column('ckey',      String(32))
    last_ip =   Column('last_ip',   BigInteger())
    last_cid =  Column('last_cid',  BigInteger())
    firtseen =  Column('firstseen', DateTime())
    lastseen =  Column('lastseen',  DateTime())
    flags =     Column('flags',     Integer()) #TINYINT

    bans =          relationship('Ban',                     back_populates='player', order_by="desc(Ban.id)")
    connections =   relationship('Connection',              back_populates='player', order_by="desc(Connection.id)")
    saves =         relationship('CloudSave',               back_populates='player')
    data =          relationship('CloudData',               back_populates='player')
    participation = relationship('Participation_Record',    back_populates='player', lazy="dynamic")

    def __init__(self, ckey, ip, cid):
        self.ckey = ckey
        self.last_ip = ip
        self.last_cid = cid
        self.firtseen = datetime.datetime.utcnow()
        self.lastseen = self.firtseen
        self.flags = 0

    @classmethod
    def from_ckey(cls, ckey, session: sqlalchemy.orm.Session):
        try:
            return session.query(cls).filter(cls.ckey == ckey).one()
        except NoResultFound:
            return None

    def get_historic_inetaddr(self, session: sqlalchemy.orm.Session, return_type = RET_INT):
        """
        Returns historical IP data about the player.
        See statics.database for return types

        TODO rewrite this docstring.
        """
        x: list = list(session.query(Connection).filter(Connection.ckey == self.ckey))
        if(return_type == RET_CON):
            return x
        ip_list: list = list()
        if(return_type == RET_STR):
            for y in x:
                ip_list.append(helpers.ip_getstr(y.ip))
        else:
            for y in x:
                ip_list.append(y.ip)
        return ip_list

    def get_historic_cid(self, session: sqlalchemy.orm.Session, return_type = RET_INT):
        """
        Returns historical IP data about the player.
        """
        x: list = list(session.query(Connection).filter(Connection.ckey == self.ckey))
        if(return_type == RET_CON):
            return x
        cid_list: list = list()
        for y in x:
            cid_list.append(y.cid)
        return cid_list



class Ban(decbase):
    __tablename__ = 'bans'

    id =        Column('id',            Integer(),      primary_key=True)
    ckey =      Column('ckey',          String(32),     ForeignKey('players.ckey'))
    ip =        Column('ip',            BigInteger())
    cid =       Column('cid',           BigInteger())
    akey =      Column('akey',          String(32))
    oakey =     Column('oakey',         String(32))
    reason =    Column('reason',        String())
#   mins =      Column('mins',          BigInteger())#WHAT, YOU THINK THE OLDEST SS13 SERVER WOULDN'T HAVE SOME SORT OF MEGAJANK LIKE THIS?!
    timestamp = Column('timestamp',     BigInteger())#YOU'DE THINK WE'D USE A TIMESTAMP FOR THIS?! HAHAHAHAH NO THIS IS ACTUALLY THE TIMESTAMP YOU GET UNBANNED. IT'S STORED AS A BYOND ERA COUNT OF MINUTES.
    #IT'S TO THE POINT WHERE WE CAN'T EVEN ISSUE MINUTE-ACCURATE BANS ANYMORE, WE'RE USUALLY OFF BY ANYWHERE AROUND ±3 MINUTES. THIS ENTIRE SYSTEM IS A J O K E
    previous =  Column('previous',      Integer())
    chain =     Column('chain',         Integer())
    removed =   Column('removed',       Integer())


    player = relationship('Player', back_populates='bans')

    def __init__(self,ckey,ip,cid,akey,oakey,reason,timestamp,previous,chain):
        self.ckey = ckey
        self.ip = ip
        self.cid = cid
        self.akey = akey
        self.oakey = oakey
        self.reason = reason
        self.timestamp = timestamp
        self.previous = previous
        self.chain = chain

    @classmethod
    def from_id(cls, session, id):
        """
        Retrieve a ban from it's database ID.
        """
        try:
            return session.query(cls).filter(cls.id == id).one()
        except NoResultFound:
            return None


class Connection(decbase):
    __tablename__ = 'connection'

    id =        Column('id',            Integer(),      primary_key=True)
    ckey =      Column('ckey',          String(32),     ForeignKey('players.ckey'))
    ip =        Column('ip',            BigInteger())
    cid =       Column('cid',           BigInteger())
    timestamp = Column('timestamp',     DateTime(),     default=datetime.datetime.utcnow)
    initial =   Column('initial',       Integer())#BOOL
    round =     Column('round',         Integer(),      ForeignKey('rounds.id'))

    round_entry =     relationship('Round_Entry', back_populates='connections')


    player = relationship('Player', back_populates='connections')

    def __init__(self, ckey, ip, cid, initial, round):
        self.ckey = ckey
        self.ip = ip
        self.cid = cid
        self.initial = initial
        self.round = round



class CloudSave(decbase):
    __tablename__ = 'cloudsaves'

    id =        Column('id',            Integer(),      primary_key=True)
    ckey =      Column('ckey',          String(32),     ForeignKey('players.ckey'))
    save_name = Column('save_name',     String())
    save =      Column('save',          String())

    player =    relationship('Player', back_populates='saves')

    def __init__(self, ckey, save_name, save):
        self.ckey = ckey
        self.save_name = save_name
        self.save = save

class CloudData(decbase):
    __tablename__ = 'clouddata'

    id =        Column('id',            Integer(),      primary_key=True)
    ckey =      Column('ckey',          String(32),     ForeignKey('players.ckey'))
    key =       Column('key',           String())
    value =     Column('value',         String())

    player =    relationship('Player', back_populates='data')

    def __init__(self, ckey, key, value):
        self.ckey = ckey
        self.key = key
        self.value = value

#This struct is mercifully ephemeral and entirely managed by the API system.
class Round_Entry(decbase):
    __tablename__ = 'rounds'

    id =            Column('id',                    Integer(),      primary_key=True)
    server_id =     Column('server_id',             String())
    server_key =    Column('server_key',            String())
    start_name =    Column('starting_station_name', String())
    start_stamp =   Column('start_stamp',           DateTime())
    end_name =      Column('ending_station_name',   String())
    end_stamp =     Column('end_stamp',             DateTime())
    mode =          Column('mode',                  String())
    reason =        Column('reason',                String())

    connections =   relationship('Connection', back_populates='round_entry')

    def __init__(self, server_id, server_key, start_name, start_stamp):
        self.server_id = server_id
        self.server_key = server_key
        self.start_name = start_name
        self.start_stamp = start_stamp

    @classmethod
    def from_id(cls, session, id):
        """
        Retrieves a round from it's id.
        """
        try:
            return session.query(cls).filter(cls.id == id).one()
        except NoResultFound:
            return None

    @classmethod
    def get_latest(cls, session, tag):
        """
        Retrieves the latest round of a particular server, by server ID.
        """
        #I pray to god that this never breaks.
        return session.query(cls).filter(cls.server_id == tag).order_by(cls.id.desc()).first()

class Participation_Record(decbase):
    __tablename__ = 'participation'

    id =        Column('id',            Integer(),      primary_key=True)
    ckey =      Column('ckey',          String(32),     ForeignKey('players.ckey'))
    recordtype =Column('record_type',   String())
    value =     Column('count',         Integer())

    player =    relationship('Player', back_populates='participation')

    def __init__(self, ckey, record_type, value):
        self.ckey = ckey
        self.recordtype = record_type
        self.value = value