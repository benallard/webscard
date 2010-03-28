from webscard.implementations import pyscard

class Implementation(pyscard.Implementation):

    super = pyscard.Implementation

    taken = {}

    def __init__(self, readerpercontext = 1):
        self.limit = readerpercontext

    def SCardListReaders(self, hContext, ReaderGroup):
        hresult, readers = self.super.SCardListReaders(self, hContext, ReaderGroup)
        if hresult == 0:
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
        return self.super.SCardReleaseContext(self, hContext)

    def SCardConnect(self, hContext, zreader, dwShared, dwProtocol):
        if not self.taken[zreader] == hContext:
            # Hep ! Reader does not exists
            zreader = "--%s--" % zreader
        return self.super.SCardConnect(self, hContext, zreader, dwShared, dwProtocol)
