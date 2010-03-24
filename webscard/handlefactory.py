"""
As handles are internaly usd to keep track of the implementation and for logging
It is handy to make them unique.
This module cares about that and keep record of the implementation that belong 
to one handle
"""

import random

RECORDFILENAME = "/tmp/WebScard.handles"

impls = {}
real = {}

def getauniquehandle(current, impl):
    res = current
    while res in impls:
        res = random.randint(0,2**32 - 1)
    impls[res] = impl
    real[res] = current
    f = open(RECORDFILENAME, 'a')
    f.write("%d\n" % res)
    f.close()
    return res

def getimplfor(handle):
    return impls[handle]

def getreal(handle):
    return real[handle]

def removeimplfor(handle):
    impl = impls[handle]
    impls[handle] = None
    del impl

def populatefromoldhandles():
    try:
        f = open(RECORDFILENAME, 'r')
        for handle in f:
            impls[int(handle)] = None
        f.close()
    except IOError:
        pass

populatefromoldhandles()
