from smartcard.scard import *

class Implementation:
    
    def SCardEstablishContext(self, dwScope):
        return SCardEstablishContext( dwScope )

    def SCardListReaders(self, hContext, ReaderGroup):
        return SCardListReaders(hContext, ReaderGroup)

    def SCardReleaseContext(self, hContext):
        return SCardReleaseContext(hContext)

    def SCardConnect(self, hContext, zreader, dwShared, dwProtocol):
        return SCardConnect(hContext, zreader, dwShared, dwProtocol)

    def SCardStatus(self, hCard):
        return SCardStatus(hCard)

    def SCardBeginTransaction(self, hCard):
        return SCardBeginTransaction(hCard)

    def SCardEndTransaction(self, hCard, dwDisposition):
        return SCardEndTransaction(hCard, dwDisposition)

    def SCardTransmit(self, hContext, dwProtocol, apdu):
        return SCardTransmit(hContext, dwProtocol, apdu)

    def SCardDisconnect(self, hCard, dwDisposition):
        return SCardDisconnect(hCard, dwDisposition)
