import hashlib

API_KEY = "API_TOK"
CLOUD_KEY = "STRING_OF_SHIT" #This one isn't even encrypted...

ACTIVE_SERVER = "127.0.0.1"
ACTIVE_PORT = 20005
MARIADB_SERVER = "127.0.0.1"
MARIADB_PORT = 3306
MARIADB_USER = "root"
MARIADB_PASS = "dum" #This is hilariously insecure probably.
MARIADB_DBNAME = "goonhub"

CALLBACK_TIMEOUT = 10

#Config Internal Transformations
API_KEY = hashlib.md5(API_KEY.encode('utf-8')).hexdigest()
