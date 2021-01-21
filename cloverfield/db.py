from cloverfield.settings import cfg
from cloverfield.util.helpers import ip_getstr
from cloverfield.statics.database import * # pylint: disable=unused-wildcard-import
from cloverfield.extensions import sqlalchemy_ext

from sqlalchemy import * # pylint: disable=unused-wildcard-import

from sqlalchemy.orm import relationship
from sqlalchemy.orm.exc import NoResultFound

from urllib.parse import quote

import datetime
import collections


session = sqlalchemy_ext.session
decbase = sqlalchemy_ext.Model

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
    notes =         relationship('PlayerNote',              back_populates='player', order_by="desc(PlayerNote.id)")
    jobexp =        relationship('JobExperience',           back_populates='player', lazy="dynamic")
    jobbans =       relationship('JobBan',                  back_populates='player', lazy="dynamic")

    def __init__(self, ckey, ip, cid):
        self.ckey = ckey
        self.last_ip = ip
        self.last_cid = cid
        self.firtseen = datetime.datetime.utcnow()
        self.lastseen = self.firtseen
        self.flags = 0

    @classmethod
    def add(cls, ckey, ip, cid):
        """
        Construct a new entry to `players`.
        """
        player = cls(
            ckey,
            ip,
            cid
        )
        session.add(player)
        session.commit()
        return player

    @classmethod
    def from_ckey(cls, ckey):
        return session.query(cls).filter(cls.ckey == ckey).one_or_none()

    def get_historic_inetaddr(self, return_type = RET_INT):
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
                ip_list.append(ip_getstr(y.ip))
        else:
            for y in x:
                ip_list.append(y.ip)
        return ip_list

    def get_historic_cid(self, return_type = RET_INT):
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
    timestamp = Column('timestamp',     BigInteger())#YOU'DE THINK WE'D USE A TIMESTAMP FOR THIS?! HAHAHAHAH NO THIS IS ACTUALLY THE TIMESTAMP YOU GET UNBANNED. IT'S STORED AS A BYOND ERA COUNT OF MINUTES.
    #IT'S TO THE POINT WHERE WE CAN'T EVEN ISSUE MINUTE-ACCURATE BANS ANYMORE, WE'RE USUALLY OFF BY ANYWHERE AROUND ±3 MINUTES. THIS ENTIRE SYSTEM IS A J O K E
    previous =  Column('previous',      Integer())
    chain =     Column('chain',         Integer())
    removed =   Column('removed',       Integer(),  default=0)


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

    @classmethod
    def add(cls,ckey,ip,cid,akey,oakey,reason,timestamp,previous,chain):
        ban = cls(
            ckey,
            ip,
            cid,
            akey,
            oakey,
            reason,
            timestamp,
            previous,
            chain
        )
        session.add(ban)
        session.commit()
        return ban

    def remove(self):
        """
        Remove(Delete) a note, retains it's entry in the database.
        sets removed to 1
        """
        self.removed = 1
        session.commit()

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

    @classmethod
    def add(cls, ckey, ip, cid, record, round_id):
        """
        Log the connection to the `connection` table. The backbone of ban checking.

        Also handles round seen tracking.
        """

        conlog = cls(
            ckey,
            ip,
            cid,
            record,
            round_id
        )
        session.add(conlog)

        if record: #First connection this round, track the fact that they have at least seen it.
            rec_sen: Participation_Record = session.query(Participation_Record).filter(Participation_Record.ckey == ckey).filter(Participation_Record.recordtype == "seen_basic").one_or_none()
            if rec_sen is None: #New player, Fill in the part of their record we care about right now.
                rec_sen = Participation_Record.add(
                    ckey,
                    "seen_basic",
                    0)

            rec_sen.record()
        return conlog


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

    @classmethod
    def add(cls, ckey, save_name, save):
        sav = cls(
            ckey,
            save_name,
            save
        )
        session.add(sav)
        session.commit()
        return sav

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

    @classmethod
    def add(cls, ckey, key, value):
        dat = cls(
            ckey,
            key,
            value
        )
        session.add(dat)
        session.commit()
        return dat

    def update(self, val):
        """
        Update the current value of this data unit.
        Must be provided in usable form.
        """
        self.value = val
        session.commit()

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

    @classmethod
    def add(cls, server_id, server_key, start_name, start_stamp):
        rnd = cls(
            server_id,
            server_key,
            start_name,
            start_stamp
        )
        session.add(rnd)
        session.commit()
        return rnd

    def mark_end(self, gname, gmode, greason):
        reason = greason
        if greason == 3:
            session.commit()
            return
        end_name = gname
        mode = gmode
        end_stamp = datetime.datetime.utcnow()
        session.commit()
        return


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

    @classmethod
    def add(cls, ckey, record_type, value):
        record = cls(
            ckey,
            record_type,
            value
        )
        session.add(record)
        session.commit()
        return record

    def record(self):
        """
        Record a participation event
        (Increment by one.)
        """
        self.value += 1
        session.commit()

class PlayerNote(decbase):
    __tablename__ = 'notes'

    id =            Column('id',            Integer(),  primary_key=True)
    server_key =    Column('server_key',    Integer())
    server_id =     Column('server_id',     String())
    ckey =          Column('ckey',          String(32), ForeignKey('players.ckey'))
    akey =          Column('akey',          String(32))
    note =          Column('note',          String())
    deleted =       Column('deleted',       Integer(),  default=0)

    player =    relationship('Player', back_populates='notes')

    def __init__(self, server_key, server_id, ckey, akey, note):
        self.server_key = server_key
        self.server_id = server_id
        self.ckey = ckey
        self.akey = akey
        self.note = note

    @classmethod
    def from_id(cls, session, id):
        """
        Retrieve a note from it's database ID.
        """
        try:
            return session.query(cls).filter(cls.id == id).one()
        except NoResultFound:
            return None

    @classmethod
    def add(cls, server_key, server_id, ckey, akey, note_txt):
        note = cls(
            server_key,
            server_id,
            ckey,
            akey,
            note_txt
        )
        session.add(note)
        session.commit()
        return note

    def remove(self):
        """
        Remove(Delete) a note, retains it's entry in the database.
        sets deleted to 1
        """
        self.deleted = 1
        session.commit()

class JobExperience(decbase):
    __tablename__ = 'jobtracking'

    id =            Column('id',            Integer(),  primary_key=True)
    ckey =          Column('ckey',          String(32), ForeignKey('players.ckey'))
    key =           Column('key',           String())
    val =           Column('value',         Integer())

    player =    relationship('Player', back_populates='jobexp')

    def __init__(self, ckey, key, val):
        self.ckey = ckey
        self.key = key
        self.val = val

    @classmethod
    def add(cls, ckey, key, val):
        exp = cls(
            ckey,
            key,
            val
        )
        session.add(exp)
        session.commit()
        return exp

    #TODO If this ever gets a public facing version, add a method to grab all of a certain key's entries for ranking.

class JobBan(decbase):
    __tablename__ = 'jobban'

    id =            Column('id',            Integer(),  primary_key=True)
    ckey =          Column('ckey',          String(32), ForeignKey('players.ckey'))
    rank =          Column('rank',          String())
    akey =          Column('akey',          String())
    issue_time =    Column('issue_time',    DateTime(), default=datetime.datetime.utcnow)
    remove_time =   Column('remove_time',   DateTime())
    removed =       Column('removed',       Integer(),  default=0)
    server_id =     Column('server_id',     String())

    player =    relationship('Player', back_populates='jobbans')

    def __init__(self, ckey, rank, akey, server_id):
        self.ckey = ckey
        self.rank = rank
        self.akey = akey
        self.server_id = server_id

    @classmethod
    def add(cls, ckey, rank, akey, server_id):
        ban = cls(
            ckey,
            rank,
            akey,
            server_id
        )
        session.add(ban)
        session.commit()
        return ban
    def remove(self):
        """
        Remove(Delete) a job ban, retains it's entry in the database.
        sets removed to 1.
        sets deletion time.
        """
        self.removed = 1
        self.remove_time = datetime.datetime.utcnow()
        session.commit()
