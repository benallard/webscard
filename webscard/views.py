

try:
    import simplejson as json
except:
    import json

from webscard import implchooser
from webscard import logger

from webscard.utils import expose, render
from webscard.handlefactory import getauniquehandle, getimplfor, getreal

@expose('/')
def welcome(request):
    return render(request, "Welcome to the universal SCard Web Proxy")

@expose('/EstablishContext', defaults={'dwScope': 0})
@expose('/EstablishContext/<int:dwScope>')
def establishcontext(request, dwScope):
    impl = implchooser.chooseone()
    hresult, hContext = impl.SCardEstablishContext(dwScope)
    hContext = getauniquehandle(hContext, impl)
    logger.loginput(__name__, hContext, dwScope=dwScope)
    logger.logoutput(__name__, hContext, hresult=hresult, hContext=hContext)
    return render(request, {"hresult":hresult, "hcontext":hContext})

@expose('/<int:handle>/ListReaders', defaults={'mszGroups': "[]"})
@expose('/<int:handle>/ListReaders/<mszGroups>')
def listreaders(request, handle, mszGroups):
    impl = getimplfor(handle)
    mszGroups = json.loads(mszGroups)
    hContext = getreal(handle)
    logger.loginput(__name__, handle, readergroup=mszGroups)
    hresult, readers = impl.SCardListReaders( hContext, mszGroups )
    logger.logoutput(__name__, handle, hResult=hresult, mszReaders=readers)
    return render(request, {"hresult":hresult, "readers":readers})


@expose('/<int:handle>/Connect/<szReader>',
        defaults={'dwSharedMode': 2, 'dwPreferredProtocol': 3})
@expose('/<int:handle>/Connect/<szReader>/<int:dwSharedMode>',
        defaults={'dwPreferredProtocol': 3})
@expose('/<int:handle>/Connect/<szReader>/<int:dwSharedMode>/<int:dwPreferredProtocol>')
def connect(request, handle, szReader, dwSharedMode, dwPreferredProtocol):
    impl = getimplfor(handle)
    hContext = getreal(handle)
    szReader = str(szReader)
    hresult, hCard, dwActiveProtocol = impl.SCardConnect(
        hContext, szReader, dwSharedMode, dwPreferredProtocol)
    hCard = getauniquehandle(hCard, impl)
    return render(request, {"hresult":hresult, "hCard":hCard,
                            "dwActiveProtocol":dwActiveProtocol})

@expose('/<int:handle>/Transmit/<apdu>', defaults={'dwProtocol': 2})
@expose('/<int:handle>/Transmit/<int:dwProtocol>/<apdu>')
def transmit(request, handle, dwProtocol, apdu):
    impl = getimplfor(handle)
    hCard = getreal(handle)
    hresult, response = impl.SCardTransmit(hCard, dwProtocol, json.loads(apdu))
    return render(request, {"hresult": hresult, "response": response})

@expose('/<int:handle>/Disconnect', defaults={'dwDisposition': 0})
@expose('/<int:handle>/Disconnect/<int:dwDisposition>')
def disconnect(request, handle, dwDisposition):
    impl = getimplfor(handle)
    hCard = getreal(handle)
    hresult = impl.SCardDisconnect(hCard, dwDisposition)
    return render( request, {"hresult": hresult})

@expose('/<int:handle>/ReleaseContext')
def releasecontext(request, handle):
    impl = getimplfor(handle)
    hContext = getreal(handle)
    logger.loginput(__name__, handle)
    hresult = impl.SCardReleaseContext(hContext)
    logger.logoutput(__name__, handle, hresult=hresult)
    return render(request, {"hresult":hresult})
        
@expose('/<int:handle>')
def log(request, handle):
    pass
