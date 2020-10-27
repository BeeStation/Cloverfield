import hashlib


#General Routes
API_KEY = "API_TOK"
#Cloud Saves #This one isn't even encrypted...
CLOUD_KEY = "STRING_OF_SHIT"
#Literally just round start and end. #kill me now
HUBLOG_KEY = "THREE_GODDAMN_TOKENS"
#Player Notes
NOTES_KEY = "AUTH_NOTES"
#SEC Ban Panel Token
US_KEY = "WEB_TOK"

#Secure HMAC Secret.
US_SECRET = "DEV_SECRET_NO_PROD"


ACTIVE_SERVER = "127.0.0.1"
ACTIVE_PORT = 20005

MARIADB_SERVER = "127.0.0.1"
MARIADB_PORT = 3306
MARIADB_USER = "root"
MARIADB_PASS = "dum" #This is hilariously insecure probably.
MARIADB_DBNAME = "goonhub"

CALLBACK_TIMEOUT = 10
API_REV = 1

#Config Internal Transformations
API_KEY = hashlib.md5(API_KEY.encode('utf-8')).hexdigest()
HUBLOG_KEY = hashlib.md5(HUBLOG_KEY.encode('utf-8')).hexdigest()


