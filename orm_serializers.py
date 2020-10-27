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
