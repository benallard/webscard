import time
import inspect

record = {}

def loginput(handle, **params):
     if 'time' not in params:
        params['time'] = time.time()
     function = inspect.stack()[1][3]
     try:
         handlerec = record[handle]
     except KeyError:
         handlerec = record[handle] = []     
     handlerec.append({function:{'input': params}})

def logoutput(handle, hresult, **params):
    if 'time' not in params:
        params['time'] = time.time()
    function = inspect.stack()[1][3]
    params['hresult'] = hresult

    index = -1
    current = record[handle][index]
    while not function in current:
        index -= 1
        if index == -len(record[handle]):
            raise KeyError(index)
        current = record[handle][index]

    current = current[function]
    current['output'] = params
    current['duration'] = current['output']['time'] - current['input']['time']
    

def getlogsfor(handle):
    return record[handle]
