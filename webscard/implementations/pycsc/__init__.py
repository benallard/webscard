"""
PyC/SC is a complete Python implementation of the SubSystem

I guess it has dependencies on pythoncard to use applets

"""
import random

from webscard.implementations.pycsc.reader import Reader
from webscard.implementations.pycsc.token import Token

from smartcard import scard # for error values

class PyCSC(object):

    def __init__(self, name, config):
        self.name = name
        self.config = config
        self.reader = Reader(name, config)
        self.token = Token(name, config)
        self.name = name
        self.contexts = []

    def SCardEstablishContext(self, dwScope):
        newcontext = random.randint(0, 0xffffffff)
        self.contexts.append(newcontext)
        return 0, newcontext

    def SCardReleaseContext(self, hContext):
        try:
            self.contexts.remove(hContext)
            res = scard.SCARD_S_SUCCESS
        except ValueError:
            res = scard.SCARD_E_INVALID_HANDLE
        return res

    def SCardListReaders(self, hContext, ReaderGroup):
        return 0, [self.reader.name]

    def SCardCancel(self, hContext):
        return 0

    def SCardGetStatusChange(self, hContext, dwTimeout, rgReaderStates):
        return 0

    def SCardConnect(self, hContext, zreader, dwShared, dwProtocol):
        if zreader == self.reader.name:
            return self.reader.Connect(hContext, dwhared, dwProtocol)
        return 0, 0, self.reader.protocol

    def SCardReconnect(self, hCard, dwSharedMode, dwPreferredProtocols, dwInitialisations):
        pass

    def SCardControl(self, hCard, dwControlCode, inBuffer):
        pass

    def SCardStatus(self, hCard):
        return self.cards[hCard].Status()
        return 0, self.reader.name, 52, self.reader.protocol, self.token.ATR

    def SCardBeginTransaction(self, hCard):
        return 0

    def SCardTransmit(self, hCard, dwProtocol, apdu):
        return 0, [0x90, 0x00]

    def SCardEndTransaction(self, hCard, dwDisposition):
        return 0

    def SCardDisconnect(self, hCard, dwDisposition):
        return 0
