import random, threading

from smartcard import scard # for constants

from webscard.implementations.pycsc.token import Token

def flag_set(flag, flags):
    return flag == flag & flags

class Reader(object):
    name = "PyC/SC Reader 0"
    def __init__(self, name, config):
        self.token = Token(name, config)
        self.protocol = config.getinteger('%s.protocol' % name, 2)
        self.cards = {}
        self.lockedby = 0
        # reentrant to authorize nested transactions
        self.transaction = threading.RLock()

    def Connect(self, share, protocols):
        card = random.randint(1, 0xffff)
        protocol = 0

        if flag_set(scard.SCARD_PROTOCOL_T1, protocols):
            protocol = scard.SCARD_PROTOCOL_T1
        elif flag_set(scard.SCARD_PROTOCOL_T0, protocols):
            protocol = scard.SCARD_PROTOCOL_T0
        else:
            return scard.SCARD_E_INVALID_PARAMETER, 0, 0

        if self.lockedby != 0:
            return scard.SCARD_E_READER_UNAVAILABLE, 0, 0

        if share in (scard.SCARD_SHARE_EXCLUSIVE, scard.SCARD_SHARE_DIRECT):
            if len(self.cards) != 0:
                return scard.SCARD_E_READER_UNAVAILABLE, 0, 0
            self.lockedby = card

        self.cards[card] = protocol
        return scard.SCARD_S_SUCCESS, card, protocol

    def Disconnect(self, card, disposition):
        if card not in self.cards:
            return scard.SCARD_E_INVALID_HANDLE
        if self.lockedby == card:
            self.lockedby = 0
        self.releasetransactionlock()
        del self.cards[card]
        return scard.SCARD_S_SUCCESS

    def Reconnect(self, card, share, protocols, initialisations):
        res = self.Disconnect(card, initialisations)
        if res != scard.SCARD_S_SUCCESS:
            return res, 0
        (res, tempcard, prot) = self.Connect(share, protocols)
        if res != scard.SCARD_S_SUCCESS:
            return res, prot
        self.cards[card] = self.cards[tempcard]
        del self.cards[tempcard]
        if self.lockedby == tempcard:
            self.lockedby = card
        return res, prot

    def BeginTransaction(self, card):
        if card not in self.cards:
            return scard.SCARD_E_INVALID_HANDLE
        self.transaction.acquire()
        return scard.SCARD_S_SUCCESS

    def EndTransaction(self, card, disposition):
        if card not in self.cards:
            return scard.SCARD_E_INVALID_HANDLE
        res = scard.SCARD_E_NOT_TRANSACTED
        try:
            self.transaction.release()
            res = scard.SCARD_S_SUCCESS
        except RuntimeError:
            # res is alread set
            pass
        return res

    def releasetransactionlock(self):
        try:
            while True: self.transaction.release()
        except RuntimeError:
            pass
