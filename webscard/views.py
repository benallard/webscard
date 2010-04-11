from datetime import datetime
try:
    import simplejson as json
except:
    import json


from webscard import logger

from webscard.utils import expose, render, dbsession

from webscard.models.handle import Context, Handle
from webscard.models.session import Session

@expose('/')
def welcome(request):
    sessions = dbsession.query(Session).all()
    ss = []
    for s in sessions:
        ss.append(s.asdict())
    return render(request, {'msg':"Welcome to the universal SCard Web Proxy", 'sessions': ss})

@expose('/EstablishContext', defaults={'dwScope': 0})
@expose('/EstablishContext/<int:dwScope>')
def establishcontext(request, dwScope):
    impl = request.implementation

    before = datetime.now() # we have to do it ourself as there is no handle before
    hresult, hContext = impl.SCardEstablishContext(dwScope)
    after = datetime.now()

    dbsession.flush() # to get a session_uid
    hContext = Context(request.session, hContext, impl)
    dbsession.flush() # to get a context_uid
    logger.loginput(hContext, dwScope=dwScope, time=before)
    logger.logoutput(hContext, hresult, time=after)
    return render(request, {"hresult":hresult, "hcontext":hContext.uid})

@expose('/<int:context>/ListReaders', defaults={'mszGroups': "[]"})
@expose('/<int:context>/ListReaders/<mszGroups>')
def listreaders(request, context, mszGroups):
    hContext = Context.query.get(context)
    impl = request.implementation
    mszGroups = json.loads(mszGroups)
    logger.loginput(hContext, readergroup=mszGroups)
    hresult, readers = impl.SCardListReaders( hContext.val, mszGroups )
    logger.logoutput(hContext, hresult, mszReaders=readers)
    return render(request, {"hresult":hresult, "mszReaders":readers})


@expose('/<int:context>/Connect/<szReader>',
        defaults={'dwSharedMode': 2, 'dwPreferredProtocol': 3})
@expose('/<int:handle>/Connect/dwSharedMode/<szReader>',
        defaults={'dwPreferredProtocol': 3})
@expose('/<int:context>/Connect/<szReader>/<int:dwSharedMode>/<int:dwPreferredProtocol>')
def connect(request, context, szReader, dwSharedMode, dwPreferredProtocol):
    hContext = Context.query.get(context)
    impl = request.implementation
    szReader = str(szReader)
    logger.loginput(hContext, szReader=szReader, dwSharedMode=dwSharedMode,
                    dwPreferredProtocol=dwPreferredProtocol)
    hresult, hCard, dwActiveProtocol = impl.SCardConnect(
        hContext.val, szReader, dwSharedMode, dwPreferredProtocol)
    after = datetime.now()
    hCard = Handle(hCard, hContext)
    dbsession.flush() # to get an uid
    logger.logoutput(hContext, hresult, hCard=hCard.uid,
                     dwActiveProtocol=dwActiveProtocol, time=after)
    return render(request, {"hresult":hresult, "hCard":hCard.uid,
                            "dwActiveProtocol":dwActiveProtocol})

@expose('/<int:card>/Status')
def status(request, card):
    hCard = Handle.query.get(card)
    impl = request.implementation
    logger.loginput(hCard.context)
    hresult, readername, dwState, dwProtocol, ATR = impl.SCardStatus(hCard.val)
    logger.logoutput(hCard.context, hresult, szReaderName = readername, dwState = dwState, dwProtocol = dwProtocol, ATR = ATR)
    return render(request, {"hresult":hresult, "szReaderName":readername, 
        "dwState":dwState, "dwProtocol":dwProtocol, "ATR":ATR})

@expose('/<int:card>/BeginTransaction')
def begintransaction(request, card):
    hCard = Handle.query.get(card)
    hContext = hCard.context
    impl = request.implementation
    logger.loginput(hContext)
    hresult = impl.SCardBeginTransaction(hCard.val)
    logger.logoutput(hContext, hresult)
    return render(request, {'hresult': hresult})

@expose('/<int:card>/EndTransaction', defaults={'dwDisposition':0})
@expose('/<int:card>/EndTransaction/<int:dwDisposition>')
def endtransaction(request, card, dwDisposition):
    hCard = Handle.query.get(card)
    hContext = hCard.context
    impl = request.implementation
    logger.loginput(hContext, dwDisposition=dwDisposition)
    hresult = impl.SCardEndTransaction(hCard.val, dwDisposition)
    logger.logoutput(hContext, hresult)
    return render(request, {'hresult': hresult})


@expose('/<int:card>/Transmit/<apdu>', defaults={'dwProtocol': 2})
@expose('/<int:card>/Transmit/<int:dwProtocol>/<apdu>')
def transmit(request, card, dwProtocol, apdu):
    hCard = Handle.query.get(card)
    hContext = hCard.context
    impl = request.implementation
    apdu = json.loads(apdu)
    logger.loginput(hContext, dwProtocol=dwProtocol, apdu=apdu)
    hresult, response = impl.SCardTransmit(hCard.val, dwProtocol, apdu)
    logger.logoutput(hContext, hresult, response=response)
    return render(request, {"hresult": hresult, "response": response})

@expose('/<int:card>/Disconnect', defaults={'dwDisposition': 0})
@expose('/<int:card>/Disconnect/<int:dwDisposition>')
def disconnect(request, card, dwDisposition):
    hCard = Handle.query.get(card)
    hContext = hCard.context
    impl = request.implementation
    logger.loginput(hContext, dwDisposition=dwDisposition)
    hresult = impl.SCardDisconnect(hCard.val, dwDisposition)
    logger.logoutput(hContext, hresult)
    return render( request, {"hresult": hresult})

@expose('/<int:context>/ReleaseContext')
def releasecontext(request, context):
    hContext = Context.query.get(context)
    impl = request.implementation
    logger.loginput(hContext)
    hresult = impl.SCardReleaseContext(hContext.val)
    logger.logoutput(hContext, hresult)
    return render(request, {"hresult":hresult})
        
# name it differenty to avoid it being checked by the validator
@expose('/<int:logcontext>')
def log(request, logcontext):
    return render(request, logger.getlogsfor(logcontext))

@expose('/log', defaults={'sid':None})
@expose('/log/<int:sid>')
def logforsession(request, sid):
    if sid is None:
        sid = request.session.uid
    sess = Session.query.get(sid)
    logs = sess.asdict()
    for ctx in dbsession.query(Context).filter(Context.session_uid == sid):
        logs[ctx.uid] = logger.getlogsfor(ctx.uid)
    return render(request, logs)
