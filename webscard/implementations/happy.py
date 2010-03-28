class Implementation:
    
    def SCardEstablishContext(self, dwScope):
        return 0, 0

    def SCardListReaders(self, hContext, ReaderGroup):
        return 0, ["Happy Reader 0"]

    def SCardReleaseContext(self, hContext):
        return 0

    def SCardConnect(self, hContext, zreader, dwShared, dwProtocol):
        return 0, 0, 2

    def SCardTransmit(self, hContext, dwProtocol, apdu):
        return 0, [0x90, 0x00]

    def SCardDisconnect(self, hCard, dwDisposition):
        return 0
