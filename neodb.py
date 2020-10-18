import settings
import helpers
import sqlalchemy
from sqlalchemy import * # pylint: disable=unused-wildcard-import
from urllib.parse import quote
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, Session
from sqlalchemy.orm.exc import NoResultFound
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

    bans = relationship('Ban', back_populates='player', order_by="desc(Ban.id)")
    connections = relationship('Connection', back_populates='player', order_by="desc(Connection.id)")

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

    def get_historic_inetaddr(self, session: sqlalchemy.orm.Session):
        """
        Returns a list of IP ints associated with a player.
        """
        x: list = list(session.query(Connection).filter(Connection.ckey == self.ckey))
        return x


class Ban(decbase):
    __tablename__ = 'bans'

    id =        Column('id',            Integer(),      primary_key=True)
    ckey =      Column('ckey',          String(32),     ForeignKey('players.ckey'))
    ip =        Column('ip',            BigInteger())
    cid =       Column('cid',           BigInteger())
    akey =      Column('akey',          String(32))
    oakey =     Column('oakey',         String(32))
    reason =    Column('reason',        String())
    mins =      Column('mins',          BigInteger())
    timestamp = Column('timestamp',     DateTime(),     default=datetime.datetime.utcnow)

    player = relationship('Player', back_populates='bans')

class Connection(decbase):
    __tablename__ = 'connection'

    id =        Column('id',            Integer(),      primary_key=True)
    ckey =      Column('ckey',          String(32),     ForeignKey('players.ckey'))
    ip =        Column('ip',            BigInteger())
    cid =       Column('cid',           BigInteger())
    timestamp = Column('timestamp',     DateTime(),     default=datetime.datetime.utcnow)
    initial =   Column('initial',       Integer())#BOOL

    player = relationship('Player', back_populates='connections')

    def __init__(self, ckey, ip, cid, initial):
        self.ckey = ckey
        self.ip = ip
        self.cid = cid
        self.initial = initial
