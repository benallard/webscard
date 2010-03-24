"""
Mainly (completely) taken from the Werkzeug tutorial
"""

from werkzeug import Local, LocalManager, Response
from werkzeug.routing import Map, Rule

try:
    import simplejson as json
except ImportError:
    import json

from smartcard.scard import SCardGetErrorMessage


local = Local()
local_manager = LocalManager([local])
application = local('application')


url_map = Map()
def expose(rule, **kw):
    def decorate(f):
        kw['endpoint'] = f.__name__
        url_map.add(Rule(rule, **kw))
        return f
    return decorate

def render(request, dict):
    """ Here we could do something based on the User Agent """
    try:
        dict['HRformat'] = SCardGetErrorMessage(dict['hresult'])
    except:
        pass
    return Response(json.dumps(dict, indent=4))
