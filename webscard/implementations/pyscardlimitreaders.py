""" 
We limit pyscard to a number of reader per session
So that one session
"""

from smartcard import scard as pyscard

class Implementation(pyscard.Implementation):

    taken = {}

    def __init__(self, readerpercontext = 1):
        self.limit = readerpercontext

    def SCardListReaders(self, hContext, ReaderGroup):
        hresult, readers = pyscard.SCardListReaders(self, hContext, ReaderGroup)
        if hresult == pyscard.SCARD_SUCCESS:
            contextreaders = []
            for reader in readers:
                if reader not in self.taken:
                    if len(contextreaders) < self.limit:
                        contextreaders.append(reader)
                        self.taken[reader] = hContext
            return hresult, contextreaders
        else:
            return hresult, readers

    def SCardReleaseContext(self, hContext):
        for reader in self.taken:
            if self.taken[reader] == hContext:
                del self.taken[reader]
        return pyscard.SCardReleaseContext(self, hContext)

    def SCardConnect(self, hContext, zreader, dwShared, dwProtocol):
        if not self.taken[zreader] == hContext:
            # Hep ! Reader does not exists
            zreader = "--%s--" % zreader
        return pyscard.SCardConnect(self, hContext, zreader, dwShared, dwProtocol)

    def __getattr__(self, name):
        return getattr(pyscard, name)

    def release(self)
