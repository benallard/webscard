"""
PyC/SC is a complete Python implementation of the SubSystem

I guess it has dependencies on pythoncard to use applets

"""

class PyCSC(object):

    readername = "PyC/SC Reader 0"

    def __init__(self, name, config):
        ATR = config.get(name, 'ATR')
        
        self.name = name
        self.protocol = config.getinteger(name, 'protocol', 2)

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
