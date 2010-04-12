from datetime import datetime
import inspect

from webscard.models import operation

record = {}

def loginput(hContext, **params):
     if 'time' not in params:
        params['time'] = datetime.now()
     # get the caller name from the stack
     function = inspect.stack()[1][3]
     opclass = getclassfor(function)
     op = opclass(context = hContext, **params)
     try:
         handlerec = record[hContext.uid]
     except KeyError:
         handlerec = record[hContext.uid] = []     
     handlerec.append({function:{'input': params}})

def logoutput(hContext, hresult, **params):
    if 'time' not in params:
        params['time'] = datetime.now()
    function = inspect.stack()[1][3]
    params['hresult'] = hresult

    index = -1
    current = record[hContext.uid][index]
    while not function in current:
        index -= 1
        if index == -len(record[handle]):
            raise KeyError(index)
        current = record[hContext.uid][index]

    current = current[function]
    current['output'] = params
    current['duration'] = str(current['output']['time'] - current['input']['time'])

classdict = {
    'establishcontext': operation.EstablishContext,
    'releasecontext': operation.ReleaseContext,
}

def getclassfor(name):
    return classdict.get(name, operation.Operation)

def getlogsfor(context):
    return record[context]
