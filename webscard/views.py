import time
try:
    import simplejson as json
except:
    import json

from webscard import implementations
from webscard import logger

from webscard.utils import expose, render
from webscard.handlefactory import getauniquehandle, getimplfor, getreal, removeimplfor

@expose('/')
def welcome(request):
    return render(request, "Welcome to the universal SCard Web Proxy")

@expose('/EstablishContext', defaults={'dwScope': 0})
@expose('/EstablishContext/<int:dwScope>')
def establishcontext(request, dwScope):
    impl = implementations.getone()
    before = time.time() # we have to do it ourself as there is no handle before 
    hresult, hContext = impl.SCardEstablishContext(dwScope)
    hContext = getauniquehandle(hContext, impl)
    after = time.time() # to avoid taking the loginput in the measurmentg
    logger.loginput(hContext, dwScope=dwScope, time=before)
    logger.logoutput(hContext, hresult, hContext=hContext, time=after)
    return render(request, {"hresult":hresult, "hcontext":hContext})

@expose('/<int:handle>/ListReaders', defaults={'mszGroups': "[]"})
@expose('/<int:handle>/ListReaders/<mszGroups>')
def listreaders(request, handle, mszGroups):
    impl = getimplfor(handle)
    mszGroups = json.loads(mszGroups)
    hContext = getreal(handle)
    logger.loginput(handle, readergroup=mszGroups)
    hresult, readers = impl.SCardListReaders( hContext, mszGroups )
    logger.logoutput(handle, hresult, mszReaders=readers)
    return render(request, {"hresult":hresult, "readers":readers})


@expose('/<int:handle>/Connect/<szReader>',
        defaults={'dwSharedMode': 2, 'dwPreferredProtocol': 3})
@expose('/<int:handle>/Connect/dwSharedMode/<szReader>',
        defaults={'dwPreferredProtocol': 3})
@expose('/<int:handle>/Connect/<szReader>/<int:dwSharedMode>/<int:dwPreferredProtocol>')
def connect(request, handle, szReader, dwSharedMode, dwPreferredProtocol):
    impl = getimplfor(handle)
    hContext = getreal(handle)
    szReader = str(szReader)
    logger.loginput(handle, szReader=szReader, dwSharedMode=dwSharedMode,
                    dwPreferredProtocol=dwPreferredProtocol)
    hresult, hCard, dwActiveProtocol = impl.SCardConnect(
        hContext, szReader, dwSharedMode, dwPreferredProtocol)
    logger.logoutput(handle, hresult, hCard=hCard,
                     dwActiveProtocol=dwActiveProtocol)
    hCard = getauniquehandle(hCard, impl)
    return render(request, {"hresult":hresult, "hCard":hCard,
                            "dwActiveProtocol":dwActiveProtocol})

@expose('/<int:handle>/Status')
def status(request, handle):
    impl = getimplfor(handle)
    hCard = getreal(handle)
    logger.loginput(handle)
    hresult, readername, dwState, dwProtocol, ATR = impl.SCardStatus(hCard)
    logger.logoutput(handle, hresult, readername = readername, dwState = dwState, dwProtocol = dwProtocol, ATR = ATR)
    return render(request, {"hresult":hresult, "readername":readername, 
        "dwState":dwState, "dwProtocol":dwProtocol, "ATR":ATR})

@expose('/<int:handle>/Transmit/<apdu>', defaults={'dwProtocol': 2})
@expose('/<int:handle>/Transmit/<int:dwProtocol>/<apdu>')
def transmit(request, handle, dwProtocol, apdu):
    impl = getimplfor(handle)
    hCard = getreal(handle)
    apdu = json.loads(apdu)
    logger.loginput(handle, dwProtocol=dwProtocol, apdu=apdu)
    hresult, response = impl.SCardTransmit(hCard, dwProtocol, apdu)
    logger.logoutput(handle, hresult, response=response)
    return render(request, {"hresult": hresult, "response": response})

@expose('/<int:handle>/Disconnect', defaults={'dwDisposition': 0})
@expose('/<int:handle>/Disconnect/<int:dwDisposition>')
def disconnect(request, handle, dwDisposition):
    impl = getimplfor(handle)
    hCard = getreal(handle)
    logger.loginput(handle, dwDisposition=dwDisposition)
    hresult = impl.SCardDisconnect(hCard, dwDisposition)
    logger.logoutput(handle, hresult)
    removeimplfor(handle)
    return render( request, {"hresult": hresult})

@expose('/<int:handle>/ReleaseContext')
def releasecontext(request, handle):
    impl = getimplfor(handle)
    hContext = getreal(handle)
    logger.loginput(handle)
    hresult = impl.SCardReleaseContext(hContext)
    logger.logoutput(handle, hresult)
    removeimplfor(handle)
    return render(request, {"hresult":hresult})
        
@expose('/<int:handle>')
def log(request, handle):
    return render(request, logger.getlogsfor(handle))
