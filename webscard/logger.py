from datetime import datetime

import thread

from webscard.models import operation
from webscard.utils import dbsession

def doit(input, output):
    try:
        function, hContext, inparams = input
        hresult, outparams = output
        opclass = operation.getclassfor(function)
        op = opclass(function, hContext, **inparams)
        op.performed(hresult, **outparams)
        dbsession.add(op)
    finally:
        dbsession.flush()
        dbsession.remove()
    

def loginput(request, hContext, **params):
    if 'time' not in params:
        params['time'] = datetime.now()
    # get the caller name from the stack
    function = request.endpoint
    return (function, hContext.uid, params)

def logoutput(inparams, hresult, **params):
    if 'time' not in params:
        params['time'] = datetime.now()
    thread.start_new(doit, (inparams, (hresult, params),))
