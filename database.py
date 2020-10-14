import settings
import helpers
import MySQLdb, MySQLdb.cursors
from flask import request
#TODO: Talk to crossed about the license of nicking this.

class DBClient:
    conn		= None
    user		= None
    password	= None
    host		= None
    dbname		= None
    port		= None

    def __init__(self, user, password, host, port, dbname):
        self.user = user
        self.password = password
        self.host = host
        self.dbname = dbname
        self.port = port

    def connect(self):
        self.conn = MySQLdb.connect(user=self.user,passwd=self.password,host=self.host,db=self.dbname,port=self.port,cursorclass=MySQLdb.cursors.DictCursor)
        self.conn.autocommit(True)

    def query(self, sql, placeholders=None):
        try:
            cursor = self.conn.cursor()
            if placeholders:
                cursor.execute(sql, placeholders)
            else:
                cursor.execute(sql)
        except (AttributeError, MySQLdb.OperationalError):
            self.connect()
            cursor = self.conn.cursor()
            if placeholders:
                cursor.execute(sql, placeholders)
            else:
                cursor.execute(sql)
        return cursor

#   Game Data Handlers

    def check_exempt(self):
        x = self.query("SELECT exempt FROM players WHERE ckey = %s", [request.args.get('ckey')])
        if not x._rows.__len__() or x._rows[0]['exempt'] == 0: #Player does not exist or is not exempt.
            return False
        return True

    def log_connection(self):
        self.query("INSERT INTO `connection` (ckey,ip,cid) VALUES (%s,%s,%s)", (
            request.args.get('ckey'),
            str(helpers.ip_getint(request.args.get('ip'))),
            request.args.get('compID')
        ))


    def feedback_version(self):
        self.query("INSERT INTO `feedback-version` (ckey,agent,major,minor,server_uid,server_id) VALUES (%s,%s,%s,%s,%s,%s)", (
            request.args.get('ckey'),
            request.args.get('userAgent'),
            request.args.get('byondMajor'),
            request.args.get('byondMinor'),
            request.args.get('data_server'),
            request.args.get('data_id')
            ))

#   Debug Statements

    def test(self):
        self.query("INSERT INTO `test` (`data`) VALUES ('data')")

    def log_statement(self, route, request_object):
        self.query("INSERT INTO `test` (route,response) VALUES (%s,%s)", (route, request_object))

#Define the database unit.
conn = DBClient(
    settings.MARIADB_USER,
    settings.MARIADB_PASS,
    settings.MARIADB_SERVER,
    settings.MARIADB_PORT,
    settings.MARIADB_DBNAME
)

