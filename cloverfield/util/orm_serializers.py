from cloverfield.db import Player, Ban

from flask.json import JSONEncoder

class JSON_Goon(JSONEncoder):

    def default(self, o):
        try:
            if isinstance(o, Ban):
                if o.oakey is None: #For some reason they didn't decide to accept 'null'...
                    o.oakey = 'N/A'
                return {
                    'id': o.id,
                    'ckey': o.ckey,
                    'ip': o.ip,
                    'compID':  o.cid,
                    'akey':  o.akey,
                    'oakey':  o.oakey,
                    'reason':  o.reason,
                    'timestamp': o.timestamp,
                    'previous':  o.previous,
                    'chain':  o.chain,
                    'removed': o.removed
                    }
            iterable = iter(o)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, o)
