import random

from smartcard import scard # for constants

def flag_set(flag, flags):
    return flag == flag & flags

class Reader(object):
    name = "PyC/SC Reader 0"
    def __init__(self, name, config):
        self.protocol = config.getinteger('%s.protocol' % name, 2)
        self.cards = {}
        self.LockedBy = 0

    def Connect(self, share, protocols):
        card = random.randint(1, 0xffff)
        protocol = 0

        if flag_set(scard.SCARD_PROTOCOL_T1, protocols):
            protocol = scard.SCARD_PROTOCOL_T1
        elif flag_set(scard.SCARD_PROTOCOL_T0, protocols):
            protocol = scard.SCARD_PROTOCOL_T0
        else:
            return scard.SCARD_E_INVALID_PARAMETER, 0, 0

        if self.LockedBy != 0:
            return scard.SCARD_E_READER_UNAVAILABLE, 0, 0

        if share in (scard.SCARD_SHARE_EXCLUSIVE, scard.SCARD_SHARE_DIRECT):
            if len(self.cards) != 0:
                return scard.SCARD_E_READER_UNAVAILABLE, 0, 0
            self.LockedBy = card

        self.cards[card] = protocol
        return scard.SCARD_S_SUCCESS, card, protocol

    def Disconnect(self, card, disposition):
        if card not in self.cards:
            return scard.SCARD_E_INVALID_HANDLE
        if self.LockedBy == card:
            self.LockedBy = 0
        del self.cards[card]
        return scard.SCARD_S_SUCCESS

    def Reconnect(self, card, share, protocols, initialisations):
        pass
