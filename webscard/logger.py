import time
import inspect

record = {}

def loginput(hContext, **params):
     if 'time' not in params:
        params['time'] = time.time()
     function = inspect.stack()[1][3]
     try:
         handlerec = record[hContext.uid]
     except KeyError:
         handlerec = record[hContext.uid] = []     
     handlerec.append({function:{'input': params}})

def logoutput(hContext, hresult, **params):
    if 'time' not in params:
        params['time'] = time.time()
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
    current['duration'] = current['output']['time'] - current['input']['time']
    

def getlogsfor(context):
    return record[context]
