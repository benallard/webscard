from smartcard.scard import *

class PyScardImpl:
    
    def SCardEstablishContext(self, dwScope):
        return SCardEstablishContext( dwScope )

    def SCardListReaders(self, hContext, ReaderGroup):
        return SCardListReaders(hContext, ReaderGroup)

    def SCardReleaseContext(self, hContext):
        return SCardReleaseContext(hContext)
