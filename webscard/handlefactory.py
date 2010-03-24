import random

"""
As handles are internaly usd to keep track of the implementation and for logging
It is handy to make them unique.
This module cares about that and keep record of the implementation that belong 
to one handle
"""

impls = {}
real = {}

def getauniquehandle(current, impl):
    res = current
    while res in impls:
        res = random.randint(0,2**32 - 1)
    impls[res] = impl
    real[res] = current
    return res

def getimplfor(handle):
    return impls[handle]

def getreal(handle):
    return real[handle]

def removeimplfor(handle):
    impl = impls[handle]
    impls[handle] = None
    del impl
