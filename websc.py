import werkzeug

from werkzeug.debug import DebuggedApplication

from smartcard.scard import *

import json

import implchooser
import handlefactory
import logger

class WebSC(object):
    def __init__(self):
        self.implchooser = implchooser.ImplChooser()
        self.handlefactory = handlefactory.HandleFactory()
        self.logger = logger.Logger()
        R = werkzeug.routing.Rule
        self.url_map = werkzeug.routing.Map([
            R('/', endpoint=self.welcome),
            R('/EstablishContext/<scope>', endpoint=self.establishcontext),
            R('/<handle>/ListReaders/<readergroup>', endpoint=self.listreaders),
            R('/<handle>/Transmit/<apdu>', endpoint=self.transmit),
            R('/<handle>/ReleaseContext', endpoint=self.releasecontext),
            R('/log/<handle>', endpoint=self.log),
            ])

    def welcome(self, request):
        return werkzeug.Response("Welcome to the universal SCard Web Proxy")

    def establishcontext(self, request, scope):
        impl = self.implchooser.chooseone()
        dwScope = int( scope )
        hresult, hContext = impl.SCardEstablishContext(dwScope)
        hContext = self.handlefactory.getauniqueone(hContext, impl)
        self.logger.loginput(__name__, hContext, dwScope=dwScope)
        self.logger.logoutput(__name__, hContext, hresult=hresult, hContext=hContext)
        return werkzeug.Response(json.dumps({"hresult":hresult, "hcontext":hContext, "HRformat": SCardGetErrorMessage(hresult)}))

    def listreaders(self, request, handle, readergroup):
        handle = int(handle)
        impl = self.handlefactory.getimplfor(handle)
        readergroup = json.loads(readergroup)
        hContext = self.handlefactory.getreal(handle)
        self.logger.loginput(__name__, handle, readergroup=readergroup)
        hresult, readers = impl.SCardListReaders( hContext, readergroup )
        self.logger.logoutput(__name__, handle, hresult=hresult, readers=readers)
        return werkzeug.Response(json.dumps({"hresult":hresult, "readers":readers, "HRformat": SCardGetErrorMessage(hresult)}))

    def transmit(self, request, handle, apdu):
        pass

    def releasecontext(self, request, handle):
        handle = int(handle)
        impl = self.handlefactory.getimplfor(handle)
        self.logger.loginput(__name__, handle)
        hContext = self.handlefactory.getreal(handle)
        hresult = impl.SCardReleaseContext(hContext)
        self.logger.logoutput(__name__, handle, hresult=hresult)
        return werkzeug.Response(json.dumps({"hresult":hresult, "HRformat": SCardGetErrorMessage(hresult)}))
        

    def log(self, request, handle):
        return werkzeug.Response(self.logger.getlogsfor(handle))

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
    websc = WebSC()
    application = websc.application
    return application(env, start)

def debug():
    """Start a standalone WSGI server."""

    websc = WebSC()
    app = DebuggedApplication(websc.application, evalex=True)
    
    host, port = ('0.0.0.0', 3333)

    werkzeug.run_simple(host, port, app, use_reloader=True)

if __name__ == "__main__":
    debug()
