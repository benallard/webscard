class Implementation(object):

    readername = "Happy Reader 0"
    protocol = 2
    ATR = [0x3B, 0x00]

    def SCardEstablishContext(self, dwScope):
        return 0, 0

    def SCardListReaders(self, hContext, ReaderGroup):
        return 0, [self.readername]

    def SCardReleaseContext(self, hContext):
        return 0

    def SCardConnect(self, hContext, zreader, dwShared, dwProtocol):
        return 0, 0, self.protocol

    def SCardStatus(self, hCard):
        return 0, self.readername, 52, self.protocol, self.ATR

    def SCardTransmit(self, hContext, dwProtocol, apdu):
        return 0, [0x90, 0x00]

    def SCardDisconnect(self, hCard, dwDisposition):
        return 0
