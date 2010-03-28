"""
Mainly taken from the Werkzeug tutorial
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


url_map = Map(redirect_defaults=False)
def expose(rule, **kw):
    def decorate(f):
        kw['endpoint'] = f.__name__
        url_map.add(Rule(rule, **kw))
        return f
    return decorate

def isabrowser(request):
    return "Mozilla" in request.headers['User-agent']

def render(request, dict):
    indent = isabrowser(request) and 4 or None
    try:
        dict['HRformat'] = SCardGetErrorMessage(dict['hresult'])
    except:
        pass
    return Response(json.dumps(dict, indent=indent, separators=(',', ':')))

