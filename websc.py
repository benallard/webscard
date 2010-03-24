import werkzeug

from werkzeug.debug import DebuggedApplication

from smartcard.scard import *

try:
    import simplejson as json
except:
    import json

import implchooser
from handlefactory import getauniquehandle, getimplfor, getreal
import logger

class WebSC(object):
    def __init__(self):
        R = werkzeug.routing.Rule
        self.url_map = werkzeug.routing.Map([
            R('/EstablishContext/<int:dwScope>', endpoint=self.establishcontext),
            R('/<int:handle>/ListReaders/<mszGroups>', endpoint=self.listreaders),
            R('/<int:handle>/Connect/<szReader>/<int:dwSharedMode>/<int:dwPreferredProtocol>',
              endpoint=self.connect),
            R('/<int:handle>/Transmit/<int:dwProtocol>/<apdu>', endpoint=self.transmit),
            R('/<int:handle>/Disconnect/<int:dwDisposition>', endpoint=self.disconnect),
            R('/<int:handle>/ReleaseContext', endpoint=self.releasecontext),
            R('/log/<int:handle>', endpoint=self.log),
            ])

    def welcome(self, request):
        return werkzeug.Response("Welcome to the universal SCard Web Proxy")

    def establishcontext(self, request, dwScope):
        impl = implchooser.chooseone()
        hresult, hContext = impl.SCardEstablishContext(dwScope)
        hContext = getauniquehandle(hContext, impl)
        logger.loginput(__name__, hContext, dwScope=dwScope)
        logger.logoutput(__name__, hContext, hresult=hresult, hContext=hContext)
        return werkzeug.Response(json.dumps({"hresult":hresult, "hcontext":hContext,
                                             "HRformat": SCardGetErrorMessage(hresult)}))

    def listreaders(self, request, handle, mszGroups):
        impl = getimplfor(handle)
        mszGroups = json.loads(mszGroups)
        hContext = getreal(handle)
        logger.loginput(__name__, handle, readergroup=mszGroups)
        hresult, readers = impl.SCardListReaders( hContext, mszGroups )
        logger.logoutput(__name__, handle, hResult=hresult, mszReaders=readers)
        return werkzeug.Response(json.dumps({"hResult":hresult, "readers":readers,
                                             "HRformat": SCardGetErrorMessage(hresult)}))

    def connect(self, request, handle, szReader, dwSharedMode, dwPreferredProtocol):
        impl = getimplfor(handle)
        hContext = getreal(handle)
        szReader = str(szReader)
	hresult, hCard, dwActiveProtocol = impl.SCardConnect(
            hContext, szReader, dwSharedMode, dwPreferredProtocol)
	hCard = getauniquehandle(hCard, impl)
	return werkzeug.Response(json.dumps({"hResult":hresult, "hCard":hCard,
                                             "dwActiveProtocol":dwActiveProtocol, 
                                             "HRformat": SCardGetErrorMessage(hresult)}))

    def disconnect(self, request, handle, dwDisposition):
        impl = getimplfor(handle)
        hCard = getreal(handle)
        hresult = impl.SCardDisconnect(hCard, dwDisposition)
        return werkzeug.Response(json.dumps({"hresult": hresult, 
                                             "HRformat": SCardGetErrorMessage(hresult)}))

    def transmit(self, request, handle, dwProtocol, apdu):
	impl = getimplfor(handle)
        hCard = getreal(handle)
	hresult, response = impl.SCardTransmit(hCard, dwProtocol, json.loads(apdu))
	return werkzeug.Response(json.dumps({"hresult": hresult, "response": response,
                                             "HRformat": SCardGetErrorMessage(hresult)}))
        

    def releasecontext(self, request, handle):
        impl = getimplfor(handle)
        hContext = getreal(handle)
        logger.loginput(__name__, handle)
        hresult = impl.SCardReleaseContext(hContext)
        logger.logoutput(__name__, handle, hresult=hresult)
        return werkzeug.Response(json.dumps({"hresult":hresult,
                                             "HRformat": SCardGetErrorMessage(hresult)}))
        

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
