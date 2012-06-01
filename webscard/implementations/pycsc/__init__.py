"""
PyC/SC is a complete Python implementation of the SubSystem

This only manage Contexts and make some parameter checking.

All the rest is delegated to the reader.

"""
import random

from webscard.implementations.pycsc.reader import Reader

from smartcard import scard # for error values

class PyCSC(object):

    def __init__(self, name, config):
        self.name = name
        self.config = config
        self.reader = Reader(name, config)
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
        return scard.SCARD_S_SUCCESS, [self.reader.name]

    def SCardConnect(self, hContext, zreader, dwShared, dwProtocol):
        """ check parameters and delegate to reader """
        if hContext not in self.contexts:
            return scard.SCARD_E_INVALID_HANDLE, 0, 0
        if zreader != self.reader.name:
            return scard.SCARD_E_UNKNOWN_READER, 0, 0

        return self.reader.Connect(dwShared, dwProtocol)

    def SCardDisconnect(self, hCard, dwDisposition):
        """ delegate to reader """
        return self.reader.Disconnect(hCard, dwDisposition)

    def SCardReconnect(self, hCard, dwSharedMode, dwPreferredProtocols, dwInitialisations):
        """ delegate to reader """
        return self.reader.Reconnect(hCard, dwSharedMode, dwPreferredProtocols)

    def SCardBeginTransaction(self, hCard):
        return self.reader.BeginTransaction(hCard)

    def SCardEndTransaction(self, hCard, dwDisposition):
        return self.reader.EndTransaction(hCard, dwDisposition)

    def SCardTransmit(self, hCard, dwProtocol, apdu):
        return self.reader.Transmit(hCard, dwProtocol, apdu)
    
    def SCardStatus(self, hCard):
        return self.reader.Status(hCard)

    def SCardGetStatusChange(self, hContext, dwTimeout, rgReaderStates):
        if hContext not in self.contexts:
            return scard.SCARD_E_INVALID_HANDLE
        return self.reader.GetStatusChange(dwTimeout, rgReaderStates)

    def SCardCancel(self, hContext):
        if hContext not in self.contexts:
            return scard.SCARD_E_INVALID_HANDLE
        return scard.SCARD_S_SUCCESS

    def SCardControl(self, hCard, dwControlCode, inBuffer):
        pass

