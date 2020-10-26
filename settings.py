import hashlib


#General Routes
API_KEY =               ""
#Cloud Saves #This one isn't even encrypted...
CLOUD_KEY =             ""
#Literally just round start and end. #kill me now
HUBLOG_KEY =            ""
#Player Notes
NOTES_KEY =             ""


ACTIVE_SERVER =         ""
ACTIVE_PORT =           0

MARIADB_SERVER =        ""
MARIADB_PORT =          0
MARIADB_USER =          ""
MARIADB_PASS =          ""
MARIADB_DBNAME =        ""

CALLBACK_TIMEOUT = 10

#Config Internal Transformations
API_KEY = hashlib.md5(API_KEY.encode('utf-8')).hexdigest()
HUBLOG_KEY = hashlib.md5(HUBLOG_KEY.encode('utf-8')).hexdigest()
