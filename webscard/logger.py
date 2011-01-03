from datetime import datetime
import inspect

from webscard.models import operation

def loginput(hContext, **params):
    if 'time' not in params:
        params['time'] = datetime.now()
    # get the caller name from the stack
    function = inspect.stack()[1][3]
    opclass = operation.getclassfor(function)
    op = opclass(function, hContext, **params)
    return op.uid

def logoutput(opuid, hresult, **params):
    if 'time' not in params:
        params['time'] = datetime.now()
    function = inspect.stack()[1][3]
    opclass = operation.getclassfor(function)
    op = opclass.query.get(opuid)
    op.performed(hresult, **params)

def getlogsfromdbfor(context):
    return context.operations
