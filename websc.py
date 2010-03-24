import werkzeug

from werkzeug.debug import DebuggedApplication

from smartcard.scard import *

try:
    import simplejson as json
except:
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
            R('/<handle>/Connect/<readername>/<mode>/<protocol>', endpoint=self.connect),
            R('/<handle>/Transmit/<protocol>/<apdu>', endpoint=self.transmit),
            R('/<handle>/Disconnect/<disposition>', endpoint=self.disconnect),
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

    def connect(self, request, handle, readername, mode, protocol):
        handle = int(handle)
        impl = self.handlefactory.getimplfor(handle)
        hContext = self.handlefactory.getreal(handle)
	hresult, hCard, dwActiveProtocol = impl.SCardConnect(hContext, str(readername), int(mode), int(protocol))
	hCard = self.handlefactory.getauniqueone(hCard, impl)
	return werkzeug.Response(json.dumps({"hresult":hresult, "hCard":hCard, "dwActiveProtocol":dwActiveProtocol, "HRformat": SCardGetErrorMessage(hresult)}))

    def disconnect(self, request, handle, disposition):
        handle = int(handle)
        impl = self.handlefactory.getimplfor(handle)
        hCard = self.handlefactory.getreal(handle)
        hresult = impl.SCardDisconnect(hCard, int(disposition))
        return werkzeug.Response(json.dumps({"hresult": hresult, "HRformat": SCardGetErrorMessage(hresult)}))

    def transmit(self, request, handle, protocol, apdu):
        handle = int(handle)
	impl = self.handlefactory.getimplfor(handle)
        hCard = self.handlefactory.getreal(handle)
	hresult, response = impl.SCardTransmit(hCard, int(protocol), json.loads(apdu))
	return werkzeug.Response(json.dumps({"hresult": hresult, "response": response, "HRformat": SCardGetErrorMessage(hresult)}))
        

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
