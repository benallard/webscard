"""
Mainly taken from the Werkzeug tutorial
"""

import imp, os, sys

try:
    import simplejson as json
except ImportError:
    import json

from werkzeug import Local, LocalManager, Response
from werkzeug.routing import Map, Rule

from sqlalchemy import MetaData
from sqlalchemy.orm import sessionmaker, scoped_session

from smartcard.scard import SCardGetErrorMessage

local = Local()
local_manager = LocalManager([local])
application = local('application')

metadata = MetaData()
dbsession = scoped_session(sessionmaker(autocommit=True), 
                           local_manager.get_ident)

url_map = Map(redirect_defaults=False)
def expose(rule, **kw):
    def decorate(f):
        kw['endpoint'] = f.__name__
        url_map.add(Rule(rule, **kw))
        return f
    return decorate

def isabrowser(request):
    try:
        return "Mozilla" in request.headers['User-Agent']
    except KeyError:
        return False

def render(request, dct):
    indent = isabrowser(request) and 4 or None
    if isabrowser(request):
        dct['HRformat'] = SCardGetErrorMessage(dct.get('hresult', 0))
    return Response(json.dumps(dct, indent=indent, separators=(',', ':')))

def Exception2JSON(e):
    return {'hresult': 0x80100003}


def main_is_frozen():
    return (hasattr(sys, "frozen") or # new py2exe
            hasattr(sys, "importers") # old py2exe
            or imp.is_frozen("__main__")) # tools/freeze

def get_main_dir():
    if main_is_frozen():
        return os.path.dirname(sys.executable)
    return os.path.dirname(sys.argv[0])

def unsigned_long(s):
    return int(s) % (2**32-1)


def hexlikeiwant(b):
    """
    >>> hexlikeiwant(10)
    '0A'
    >>> hexlikeiwant(65)
    '41'
    """
    b = hex(b)[2:].upper()
    if len(b) == 1:
        b = '0' + b
    return b

def loadpath(path, name):
    """ taken from mercurial.extensions """
    name = name.replace('.','_')
    path = os.path.expanduser(os.path.expandvars(path))
    if os.path.isdir(path):
        # module/__init__.py style
        d, f = os.path.split(path.rstrip(os.path.sep))
        fd, fpath, desc = imp.find_module(f, [d])
        return imp.load_module(name, fd, fpath, desc)
    else:
        return imp.load_source(name, path)

