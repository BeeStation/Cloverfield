from neodb import Player, Ban
from flask.json import JSONEncoder

class JSON_Goon(JSONEncoder):

    def default(self, o):
        try:
            if isinstance(o, Ban):
                if o.oakey is None: #For some reason they didn't decide to accept 'null'...
                    o.oakey = 'N/A'
                return {'ckey': o.ckey,
                    'ip': o.ip,
                    'compID':  o.cid,
                    'reason':  o.reason,
                    'oakey':  o.oakey,
                    'akey':  o.akey,

                    #Okay. All of this shit is related to evasion management.
                    #That sounds difficult. So for now we're going to blindly
                    #hardwire all of these to false.
                    #Blindly mirror the data. You don't need to understand it, just pass it like a good storage system.

                    'previous':  o.previous,
                    'chain':  o.chain
                    }
            iterable = iter(o)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, o)
