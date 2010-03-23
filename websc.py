import werkzeug

from werkzeug.debug import DebuggedApplication

import json

from smartcard.scard import *

class WebSC(object):
    def __init__(self):
        R = werkzeug.routing.Rule
        self.url_map = werkzeug.routing.Map([
            R('/', endpoint=self.welcome),
            R('/EstablishContext/<scope>', endpoint=self.establishcontext),
            R('/<handle>/ListReaders/<readergroup>', endpoint=self.listreaders),
            R('/<handle>/Transmit/<apdu>', endpoint=self.transmit),
            R('/<handle>/ReleaseContext', endpoint=self.release),
            ])

    def welcome(self, request):
        return werkzeug.Response("Welcome")

    def establishcontext(self, request, scope):
        hresult, hcontext = SCardEstablishContext(int(scope))
        return werkzeug.Response(json.dumps({"hresult":hresult, "hcontext":hcontext, "HRformat": SCardGetErrorMessage(hresult)}))

    def listreaders(self, request, context, readergroup):
        hresult, readers = SCardListReaders( long(context), eval(readergroup) )
        return werkzeug.Response(json.dumps({"hresult":hresult, "hcontext":context, "readers":readers, "HRformat": SCardGetErrorMessage(hresult)}))

    def transmit(self, request, context, apdu):
        pass

    def release(self, request, context):
        hresult = SCardReleaseContext(long(context))
        return werkzeug.Response(json.dumps({"hresult":hresult, "HRformat": SCardGetErrorMessage(hresult)}))
        

    @werkzeug.responder
    def application(self, environ, start):
        """The main application loop."""

        adapter = self.url_map.bind_to_environ(environ)
        request = werkzeug.Request(environ)
        endpoint, values = adapter.match()
        return endpoint(request, **values)

def application(env, start):
    """Detect that we are being run as WSGI application."""

    global application
    httpsc = WebSC()
    application = httpsc.application
    return application(env, start)

def debug(config=None, wiki=None):
    """Start a standalone WSGI server."""

    httpsc = WebSC()
    app = DebuggedApplication(httpsc.application, evalex=True)
    
    host, port = ('0.0.0.0', 3333)

    werkzeug.run_simple(host, port, app, use_reloader=True)

if __name__ == "__main__":
    debug()
