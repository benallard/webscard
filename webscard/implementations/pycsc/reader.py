import random, threading, textwrap, time

from smartcard import scard # for constants

from webscard.implementations.pycsc.token import Token

def flag_set(flag, flags):
    return flag == flag & flags

class Reader(object):
    name = "PyCSC Reader 0"
    def __init__(self, name, config):
        self.token = Token.get(name, config[name])
        self.protocol = config[name].get('protocol', 2)
        self.cards = {}
        self.lockedby = 0
        # reentrant to authorize nested transactions
        self.transaction = CardRLock()

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
        self.transaction.reset()
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
        self.transaction.acquire(card)
        return scard.SCARD_S_SUCCESS

    def EndTransaction(self, card, disposition):
        if card not in self.cards:
            return scard.SCARD_E_INVALID_HANDLE
        res = scard.SCARD_E_NOT_TRANSACTED
        if self.transaction.release(card):
            res = scard.SCARD_S_SUCCESS
        return res

    def Transmit(self, card, protocol, apdubytes):
        if card not in self.cards:
            return scard.SCARD_E_INVALID_HANDLE, []
        return self.token.transmit(apdubytes)

    def Status(self, card):
        if card not in self.cards:
            return scard.SCARD_E_INVALID_HANDLE, self.name, 0, 0, []
        # 0x10 is SCARD_POWERED
        return scard.SCARD_S_SUCCESS, self.name, 0x10, self.cards[card], self.token.ATR
        
    def GetStatusChange(self, timeout, readerstates):
        state = 0x10122
        atr = []
        if self.token:
            state |= scard.SCARD_STATE_PRESENT
            atr = self.token.atr
        else:
            state |= scard.SCARD_STATE_EMPTY
        time.sleep(timeout/1000)
        return scard.SCARD_S_SUCCESS, [(self.name, state, atr)]

    def __str__(self):
        return textwrap.dedent("'"+self.name + """'\
         with one token inside:
        """) + str(self.token)

class CardRLock(object):
    """ A kind of RLock, but based on hCard instead of thread """
    def __init__(self):
        self.counter = 0
        self.hCard = None
        self.lock = threading.Lock()

    def acquire(self, hCard):
        if self.hCard != hCard:
            self.lock.acquire()
            self.hCard = hCard
        self.counter += 1

    def release(self, hCard):
        if self.hCard != hCard:
            return False
        self.counter -= 1
        if self.counter == 0:
            self.lock.release()
            self.hCard = None
        return True

    def reset(self):
        if self.counter > 0:
            self.counter = 0
            self.hCard = None
            self.lock.release()
