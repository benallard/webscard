from datetime import datetime
import inspect

from webscard.models import operation

record = {}

def loginput(hContext, **params):
    if 'time' not in params:
         params['time'] = datetime.now()
    # get the caller name from the stack
    function = inspect.stack()[1][3]
    opclass = operation.getclassfor(function)
    op = opclass(function, hContext, **params)
    params['time'] = str(params['time'])
    try:
         handlerec = record[hContext.uid]
    except KeyError:
         handlerec = record[hContext.uid] = []     
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
    current = record[op.context_uid][index]
    while not function in current:
         index -= 1
         if index == -len(record[handle]):
              raise KeyError(index)
         current = record[op.context_uid][index]

    current = current[function]
    current['output'] = params
    current['duration'] = str(current['output']['time'] - current['input']['time'])


def getlogsfor(context):
    return record[context]

def getlogsforfromdb(context):
     log = []
     for op in context.operations:
          log.append(op.asdict())
     return log
