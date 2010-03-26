"""
Mainly (completely) taken from the Werkzeug tutorial
"""

from werkzeug import Local, LocalManager, Response
from werkzeug.routing import Map, Rule

from sqlalchemy import MetaData
from sqlalchemy.orm import create_session, scoped_session

try:
    import simplejson as json
except ImportError:
    import json

from smartcard.scard import SCardGetErrorMessage

local = Local()
local_manager = LocalManager([local])
application = local('application')

metadata = MetaData()
dbsession = scoped_session(lambda: create_session(application.database_engine,
    transactional=True), local_manager.get_ident)

url_map = Map(redirect_defaults=False)
def expose(rule, **kw):
    def decorate(f):
        kw['endpoint'] = f.__name__
        url_map.add(Rule(rule, **kw))
        return f
    return decorate

def render(request, dict):
    """ Here we could do something based on the request"""
    indent = 4
    if 'Indent' in request.headers:
        indent = request.headers['Indent']
        if indent == "no":
            indent = None
        else:
            indent = int(indent)
    try:
        dict['HRformat'] = SCardGetErrorMessage(dict['hresult'])
    except:
        pass
    return Response(json.dumps(dict, indent=indent, separators=(',', ':')))

