""" 
We limit pyscard to a number of reader per session
So that one session has its own (set of) reader(s)
and does not get distrurbance from other sessions
"""

from smartcard import scard as pyscard

list = []

taken = {}

def isfree():
    if not '--initialized--' in list:
        return True
    for reader in list:
        if not reader == '--initialized--':
            if not reader in taken:
                return True
    return False

def acquire(session):
    return Implementation(session)

def release(session):
    newtaken = {}
    for reader in taken:
        if not taken[reader] == session.uid:
            newtaken[reader] = taken[reader]
    taken = newtaken
            

def _filterreaders(session, readers):
    c = application.config
    limit = c.getinteger('clusterpyscard.limit', 1)
    contextreaders = []
    for reader in readers:
        if reader not in taken:
            if len(contextreaders) < limit:
                contextreaders.append(reader)
                taken[reader] = session.uid
    return contextreaders


def _connect(sesion, reader):
    if not taken[zreader] == session.uid:
        # Hep ! Reader does not exists
        reader = "--%s--" % reader
    return reader

class Implementation():
    def __init__(self, session):
        self.session = session

    def SCardListReaders(self, hContext, ReaderGroup):
        hresult, readers = pyscard.SCardListReaders(self, hContext, ReaderGroup)
        if hresult == pyscard.SCARD_SUCCESS:
            contextreaders = _filterreaders(self.session, readers)
            return hresult, contextreaders
        else:
            return hresult, []

    def SCardConnect(self, hContext, zreader, dwShared, dwProtocol):
        zreader = _connect(self.session, zreader)
        return pyscard.SCardConnect(self, hContext, zreader, dwShared, dwProtocol)

    # For all the other functions
    def __getattr__(self, name):
        return getattr(pyscard, name)
