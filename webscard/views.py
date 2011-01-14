from datetime import datetime
try:
    import simplejson as json
except:
    import json

from werkzeug import url_unquote

from webscard import logger, soap

from webscard.utils import expose, dbsession, unsigned_long
from webscard.render import render

from webscard.models.handle import Context, Handle
from webscard.models.session import Session

@expose('/')
def welcome(request):
    return render(request)

@expose('/EstablishContext', defaults={'dwScope': 0})
@expose('/EstablishContext/<int:dwScope>')
def establishcontext(request, dwScope):
    impl = request.implementation

    before = datetime.now() # we have to do it ourself as there is no handle before
    hresult, hContext = impl.SCardEstablishContext(dwScope)
    after = datetime.now()

    hContext = Context(request.session, hContext, impl)
    opuid = logger.loginput(hContext, dwScope=dwScope, time=before)
    logger.logoutput(opuid, hresult, time=after)
    return render(request, hresult=hresult, hcontext=hContext.uid)

@expose('/<int:context>/ListReaders', defaults={'mszGroups': "[]"})
@expose('/<int:context>/ListReaders/<mszGroups>')
def listreaders(request, context, mszGroups):
    hContext = Context.query.get(context)
    impl = request.implementation
    mszGroups = json.loads(url_unquote(mszGroups))
    opuid = logger.loginput(hContext, readergroup=mszGroups)
    hresult, readers = impl.SCardListReaders( hContext.val, mszGroups )
    logger.logoutput(opuid, hresult, mszReaders=readers)
    return render(request, hresult=hresult, mszReaders=readers)

@expose('/<int:context>/GetStatusChange/<rgReaderStates>', defaults={'dwTimeout':60000})
@expose('/<int:context>/GetStatusChange/<dwTimeout>/<rgReaderStates>')
def getstatuschange(request, context, dwTimeout, rgReaderStates):
    hContext = Context.query.get(context)
    impl = request.implementation
    dwTimeout = unsigned_long(dwTimeout)
    rgReaderStates = json.loads(url_unquote(rgReaderStates))
    ReaderStates = []
    for readerstate in rgReaderStates:
        name = str(readerstate[0])
        event = readerstate[1]
        res = name, event,
        try:
            atr = readerstate[2]
            res = name, event, atr
        except IndexError:
            pass
        ReaderStates.append(res)
    opuid = logger.loginput(hContext, dwTimeout=dwTimeout, rgReaderStates=ReaderStates)
    hresult, states = impl.SCardGetStatusChange( hContext.val, dwTimeout, ReaderStates )
    logger.logoutput(opuid, hresult, rgReaderStates=states)
    return render(request, hresult=hresult, rgReaderStates=states)

@expose('/<int:context>/Connect/<szReader>',
        defaults={'dwSharedMode': 2, 'dwPreferredProtocols': 3})
@expose('/<int:handle>/Connect/<szReader>/<int:dwSharedMode>',
        defaults={'dwPreferredProtocols': 3})
@expose('/<int:context>/Connect/<szReader>/<int:dwSharedMode>/<int:dwPreferredProtocols>')
def connect(request, context, szReader, dwSharedMode, dwPreferredProtocols):
    hContext = Context.query.get(context)
    impl = request.implementation
    szReader = str(url_unquote(szReader))
    opuid = logger.loginput(hContext, szReader=szReader, dwSharedMode=dwSharedMode,
                    dwPreferredProtocols=dwPreferredProtocols)
    hresult, hCard, dwActiveProtocol = impl.SCardConnect(
        hContext.val, szReader, dwSharedMode, dwPreferredProtocols)
    after = datetime.now()
    hCard = Handle(hCard, hContext)
    logger.logoutput(opuid, hresult, hCard=hCard.uid,
                     dwActiveProtocol=dwActiveProtocol, time=after)
    return render(request, hresult=hresult, hCard=hCard.uid,
                  dwActiveProtocol=dwActiveProtocol)

@expose('/<int:card>/Reconnect', defaults={"dwShareMode":2,
                                           "dwPreferredProtocols":3,
                                           "dwInitialisation": 0})
@expose('/<int:card>/Reconnect/<int:dwShareMode>',
        defaults={"dwPreferredProtocols":3, "dwInitialisation": 0})
@expose('/<int:card>/Reconnect/<int:dwShareMode>/<int:dwPreferredProtocols>',
        defaults={"dwInitialisation": 0})
@expose('/<int:card>/Reconnect/<int:dwShareMode>/<int:dwPreferredProtocols>/<int:dwInitialisation>')
def reconnect(request, card, dwShareMode, dwPreferredProtocols, dwInitialisation):
    hCard = Handle.query.get(card)
    impl = request.implementation
    opuid = logger.loginput(hCard.context, dwShareMode=dwShareMode, 
                            dwPreferredProtocols=dwPreferredProtocols, 
                            dwInitialisation=dwInitialisation)
    hresult, dwActiveProtocol = impl.SCardReconnect(hCard.val, dwShareMode, dwPreferredProtocols, dwInitialisation)
    logger.logoutput(opuid, hresult, dwInitialisation=dwInitialisation)
    return render(request, hresult=hresult, dwActiveProtocol=dwActiveProtocol)

@expose('/<int:card>/Control/<int:dwControlCode>/<inbuffer>')
def control(request, card, dwControlCode, inbuffer):
    hCard = Handle.query.get(card)
    impl = request.implementation
    inbuffer = json.loads(url_unquote(inbuffer))
    opuid = logger.loginput(hCard.context, dwControlCode=dwControlCode, inbuffer=inbuffer)
    hresult, response = impl.SCardControl(hCard.val, dwControlCode, inbuffer)
    logger.logoutput(opuid, hresult, outbuffer=response)
    return render(request, hresult=hresult, outbuffer=response)


@expose('/<int:card>/Status')
def status(request, card):
    hCard = Handle.query.get(card)
    impl = request.implementation
    opuid = logger.loginput(hCard.context)
    hresult, readername, dwState, dwProtocol, ATR = impl.SCardStatus(hCard.val)
    logger.logoutput(opuid, hresult, szReaderName = readername, dwState = dwState, dwProtocol = dwProtocol, ATR = ATR)
    return render(request, hresult=hresult, szReaderName=readername, 
                  dwState=dwState, dwProtocol=dwProtocol, ATR=ATR)


@expose('/<int:card>/BeginTransaction')
def begintransaction(request, card):
    hCard = Handle.query.get(card)
    hContext = hCard.context
    impl = request.implementation
    opuid = logger.loginput(hContext)
    hresult = impl.SCardBeginTransaction(hCard.val)
    logger.logoutput(opuid, hresult)
    return render(request, hresult=hresult)


@expose('/<int:card>/EndTransaction', defaults={'dwDisposition':0})
@expose('/<int:card>/EndTransaction/<int:dwDisposition>')
def endtransaction(request, card, dwDisposition):
    hCard = Handle.query.get(card)
    hContext = hCard.context
    impl = request.implementation
    opuid = logger.loginput(hContext, dwDisposition=dwDisposition)
    hresult = impl.SCardEndTransaction(hCard.val, dwDisposition)
    logger.logoutput(opuid, hresult)
    return render(request, hresult=hresult)


@expose('/<int:card>/Transmit/<apdu>', defaults={'dwProtocol': 2})
@expose('/<int:card>/Transmit/<int:dwProtocol>/<apdu>')
def transmit(request, card, dwProtocol, apdu):
    hCard = Handle.query.get(card)
    hContext = hCard.context
    impl = request.implementation
    apdu = json.loads(url_unquote(apdu))
    opuid = logger.loginput(hContext, dwProtocol=dwProtocol, apdu=apdu)
    hresult, response = impl.SCardTransmit(hCard.val, dwProtocol, apdu)
    logger.logoutput(opuid, hresult, response=response)
    return render(request, hresult=hresult, response=response)

@expose('/<int:card>/Disconnect', defaults={'dwDisposition': 0})
@expose('/<int:card>/Disconnect/<int:dwDisposition>')
def disconnect(request, card, dwDisposition):
    hCard = Handle.query.get(card)
    hContext = hCard.context
    impl = request.implementation
    opuid = logger.loginput(hContext, dwDisposition=dwDisposition, hCard=hCard.uid)
    hresult = impl.SCardDisconnect(hCard.val, dwDisposition)
    logger.logoutput(opuid, hresult)
    return render( request, hresult=hresult)

@expose('/<int:context>/Cancel')
def cancel(request, context):
    hContext = Context.query.get(context)
    impl = request.implementation
    opuid = logger.loginput(hContext)
    hresult = impl.SCardCancel(hContext.val)
    logger.logoutput(opuid, hresult)
    return render(request, hresult=hresult)
    

@expose('/<int:context>/ReleaseContext')
def releasecontext(request, context):
    hContext = Context.query.get(context)
    impl = request.implementation
    opuid = logger.loginput(hContext)
    hresult = impl.SCardReleaseContext(hContext.val)
    logger.logoutput(opuid, hresult)
    return render(request, hresult=hresult)

@expose('/soap/v<int:version>')
def soapv(request, version):
    """
    Our SOAP interface
    """
    method = getattr(soap, 'version%d' % version)
    return method(request)

@expose('/<int:logcontext>')
def logforcontext(request, logcontext):
    """
    Gets the logs for a particular context
    """
    ctx = Context.query.get(logcontext)
    return render(request, context=ctx)

@expose('/log', defaults={'sid':None})
@expose('/log/<int:sid>')
def logforsession(request, sid):
    """
    Get the logs for a particular session
    """
    if sid is None:
        sid = request.session.uid
    sess = Session.query.get(sid)
    return render(request, session=sess)

@expose('/sessions')
def sessionlist(request):
    sessions = dbsession.query(Session).all()
    return render(request, {'sessions': sessions})

@expose('/help')
def help(request):
    return render(request)
