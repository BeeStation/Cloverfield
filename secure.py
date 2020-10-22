from flask import request, Blueprint

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

    #Functionary terms
        #search['+column+'] = term
        #sort               = sort
        #order              = order
        #offset             = offset
        #limit              = limit
        #removed            = removed

        #Additional datapoints for serve


#Ban Retrieval API
@api_secure.route('/bans/get')
def secure_get_banpanel():
    pass


#Another annoyingly specific route. Stub and investigate later.
@api_secure.route('/bans/getPrevious')
def secure_getprevious_banpanel():
    pass

#Considerations for security:
#Use the inbound IP as a way to verify that the user is at least a player,
#if they are not, and the API key is correct, cease servicing this route until
#it is reset by a sysop.

def verify_ultrasecure():
    pass
