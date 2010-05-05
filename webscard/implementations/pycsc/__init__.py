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
        """ internaly store the context """
        newcontext = random.randint(1, 0xffffffff)
        self.contexts.append(newcontext)
        return 0, newcontext

    def SCardReleaseContext(self, hContext):
        """ remove the context from the store """
        try:
            self.contexts.remove(hContext)
            res = scard.SCARD_S_SUCCESS
        except ValueError:
            res = scard.SCARD_E_INVALID_HANDLE
        return res

    def SCardListReaders(self, hContext, ReaderGroup):
        """ our only reader name """
        if hContext not in self.contexts:
            return scard.SCARD_E_INVALID_HANDLE, []
        return 0, [self.reader.name]

    def SCardConnect(self, hContext, zreader, dwShared, dwProtocol):
        """ check parameters and delegate to reader """
        if hContext not in self.contexts:
            return scard.SCARD_E_INVALID_HANDLE, 0, 0
        if zreader != self.reader.name:
            return scard.SCARD_E_UNKNOWN_READER, 0, 0

        return self.reader.Connect(dwShared, dwProtocol)

    def SCardDisconnect(self, hCard, dwDisposition):
        return self.reader.Disconnect(hCard, dwDisposition)

    def SCardReconnect(self, hCard, dwSharedMode, dwPreferredProtocols, dwInitialisations):
        return self.reader.Reconnect(hCard, dwSharedMode, dwPreferredProtocols)

    def SCardCancel(self, hContext):
        if hContext not in self.contexts:
            return scard.SCARD_E_INVALID_HANDLE
        return 0

    def SCardGetStatusChange(self, hContext, dwTimeout, rgReaderStates):
        return 0

    def SCardControl(self, hCard, dwControlCode, inBuffer):
        pass

    def SCardStatus(self, hCard):
        return self.reader.Status(hCard)

    def SCardBeginTransaction(self, hCard):
        return 0

    def SCardTransmit(self, hCard, dwProtocol, apdu):
        return 0, [0x90, 0x00]

    def SCardEndTransaction(self, hCard, dwDisposition):
        return 0

