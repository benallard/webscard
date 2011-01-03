from os import path

try:
    import simplejson as json
except ImportError:
    import json
    
from jinja2 import Environment, FileSystemLoader

from werkzeug import Response

from smartcard.scard import SCardGetErrorMessage

#: Jinja2 Environment for our template handling
jinja_environment = Environment(loader=FileSystemLoader(
    path.join(path.dirname(__file__), 'templates')))


def isabrowser(request):
    try:
        return "Mozilla" in request.headers['User-Agent']
    except KeyError:
        return False

def render(request, dct):
    mimetype = 'text/plain'
    if isabrowser(request):
        renderer = JinjaRenderer(request)
        mimetype = 'text/html'
    else:
        renderer = JSONRenderer(request)
    return Response(renderer(dct), mimetype = mimetype)

def Exception2JSON(e):
    return {'hresult': 0x80100003}

class JSONRenderer(object):
    def __init__(self, request):
        self.indent = isabrowser(request) and 4 or None

    def __call__(self, context):
        return json.dumps(context, indent=self.indent, separators=(',', ':'))

class JinjaRenderer(object):
    def __init__(self, request):
        self.template_name = request.endpoint + ".html"
        self.request = request
        self.ctxext = {} #context extension
        self.ctxext['request'] = request

    def getsuggestions(self):
        for context in self.request.session.contexts:
            yield ('/%d/ReleaseContext' % context.uid, "Close an unused context")
        if self.request.endpoint == 'welcome':
            yield ('/EstablishContext', "Establish a new context")

    def __call__(self, context):
        context.update(self.ctxext)
        context['suggestions'] = self.getsuggestions()
        return jinja_environment.get_template(self.template_name).render(context)
