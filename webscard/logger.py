from datetime import datetime
import inspect

from webscard.models import operation

RECORD = {}

def loginput(hContext, **params):
    if 'time' not in params:
        params['time'] = datetime.now()
    # get the caller name from the stack
    function = inspect.stack()[1][3]
    opclass = operation.getclassfor(function)
    op = opclass(function, hContext, **params)
    params['time'] = str(params['time'])
    try:
        handlerec = RECORD[hContext.uid]
    except KeyError:
        handlerec = RECORD[hContext.uid] = []
    handlerec.append({function:{'input': params}})
    return op.uid

def logoutput(opuid, hresult, **params):
    if 'time' not in params:
        params['time'] = datetime.now()
    function = inspect.stack()[1][3]
    opclass = operation.getclassfor(function)
    op = opclass.query.get(opuid)
    op.performed(hresult, **params)

    params['time'] = str(params['time'])
    params['hresult'] = hresult

    index = -1
    current = RECORD[op.context_uid][index]
    while not function in current:
        index -= 1
        if index == -len(RECORD[op.context_uid]):
            raise KeyError(index)
        current = RECORD[op.context_uid][index]

    current = current[function]
    current['output'] = params
    current['duration'] = current['output']['time'] + " - " \
        +current['input']['time'] + "(ask the db)"


def getlogsfor(context):
    try:
        return RECORD[context]
    except KeyError:
        return {}

def getlogsfromdbfor(context):
    log = []
    for op in context.operations:
        log.append(op.asdict())
    return log
