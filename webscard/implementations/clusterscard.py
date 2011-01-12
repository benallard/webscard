""" 
We limit pyscard to a number of reader per session
So that one session has its own (set of) reader(s)
and does not get distrurbance from other sessions
"""

import random

from smartcard import scard as pyscard

from webscard.utils import application

#reader list
LIST = []

initialized = []

# reader : session_uid
TAKEN = {}

# sessions already served
served = []

def isfree():
    if not initialized:
        return True
    for reader in LIST:
        if reader not in TAKEN:
            return True
    print "No reader free"
    return False

def acquire(session):
    print "acquire in clusterscard"
    return Implementation(session)

def release(session):
    for reader in TAKEN:
        if TAKEN[reader] == session.uid:
            del TAKEN[reader]
    served.remove(session.uid)
            

def _filterreaders(uid, readers):
    global LIST
    global initialized
    cfg = application.config
    initialized = True
    LIST = []
    for reader in readers:
        LIST.append(reader)
    limit = cfg.getinteger('clusterscard.limit', 1)
    contextreaders = []
    if uid in served:
        for reader in readers:
            if TAKEN.get(reader) == uid:
                contextreaders.append(reader)
    else:
        free = []
        for reader in readers:
            if reader not in TAKEN:
                free.append(reader)
        contextreaders = random.sample(free, limit)
        for reader in contextreaders:
            TAKEN[reader] = uid
        served.append(uid)
    return contextreaders


def _connect(uid, reader):
    if not TAKEN.get(reader) == uid:
        print "uid is %d != %d" % (uid, TAKEN.get(reader))
        # Hep ! Reader does not exists
        reader = "--%s--" % reader
    return reader

class Implementation():
    # We shouldn't store the session there, or if we do, 
    # we want to reattach it to the db each time.
    def __init__(self, session):
        self.session_uid = session.uid

    def SCardListReaders(self, hContext, ReaderGroup):
        hresult, readers = pyscard.SCardListReaders(hContext, ReaderGroup)
        if hresult == pyscard.SCARD_S_SUCCESS:
            contextreaders = _filterreaders(self.session_uid, readers)
            return hresult, contextreaders
        else:
            return hresult, []

    def SCardConnect(self, hContext, zreader, dwShared, dwProtocol):
        zreader = _connect(self.session_uid, zreader)
        return pyscard.SCardConnect(hContext, zreader, dwShared, dwProtocol)

    # For all the other functions
    def __getattr__(self, name):
        return getattr(pyscard, name)
