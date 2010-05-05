import unittest

from smartcard import scard # for constants

from webscard import config

from webscard.implementations.pycsc.reader import Reader, flag_set

class testPyCSCReader(unittest.TestCase):
    
    def setUp(self):
        cfg = config.Config()
        cfg.add_section('pycsc')
        cfg.set('pycsc', 'ATR', '3B 00 00')
        self.reader = Reader('pycsc', cfg)

    def testHandle(self):
        self.assertEquals(scard.SCARD_E_INVALID_HANDLE,
                          self.reader.Disconnect(42, scard.SCARD_LEAVE_CARD))
        (res, card, prot) = self.reader.Connect(scard.SCARD_SHARE_SHARED, 
                                                scard.SCARD_PROTOCOL_T1)
        self.assertEquals(scard.SCARD_S_SUCCESS, res)
        self.assertEquals(scard.SCARD_PROTOCOL_T1, prot)
        
        self.assertEquals(scard.SCARD_S_SUCCESS,
                         self.reader.Disconnect(card, scard.SCARD_LEAVE_CARD))
        self.assertEquals(scard.SCARD_E_INVALID_HANDLE,
                          self.reader.Disconnect(card, scard.SCARD_LEAVE_CARD))

    def testLock(self):
        # Nothing during opened shared connection
        (res, card, prot) = self.reader.Connect(scard.SCARD_SHARE_SHARED,
                                                scard.SCARD_PROTOCOL_T1)
        self.assertEquals(scard.SCARD_S_SUCCESS, res)
        self.assertEquals(scard.SCARD_E_READER_UNAVAILABLE,
                          self.reader.Connect(scard.SCARD_SHARE_EXCLUSIVE,
                                              scard.SCARD_PROTOCOL_T1)[0])
        (res, card2, prot2) = self.reader.Connect(scard.SCARD_SHARE_SHARED,
                                                  scard.SCARD_PROTOCOL_T1)
        self.assertEquals(scard.SCARD_S_SUCCESS, res)
        self.assertEquals(scard.SCARD_S_SUCCESS,
                         self.reader.Disconnect(card, scard.SCARD_LEAVE_CARD))
        self.assertEquals(scard.SCARD_S_SUCCESS,
                         self.reader.Disconnect(card2, scard.SCARD_LEAVE_CARD))
        
        # only one exclusive
        (res, card, prot) = self.reader.Connect(scard.SCARD_SHARE_EXCLUSIVE,
                                                scard.SCARD_PROTOCOL_T1)
        self.assertEquals(scard.SCARD_S_SUCCESS, res)
        self.assertEquals(scard.SCARD_E_READER_UNAVAILABLE,
                          self.reader.Connect(scard.SCARD_SHARE_EXCLUSIVE,
                                              scard.SCARD_PROTOCOL_T1)[0])
        self.assertEquals(scard.SCARD_E_READER_UNAVAILABLE,
                          self.reader.Connect(scard.SCARD_SHARE_DIRECT,
                                              scard.SCARD_PROTOCOL_T1)[0])
        self.assertEquals(scard.SCARD_E_READER_UNAVAILABLE,
                          self.reader.Connect(scard.SCARD_SHARE_SHARED,
                                              scard.SCARD_PROTOCOL_T1)[0])
        self.assertEquals(scard.SCARD_S_SUCCESS,
                         self.reader.Disconnect(card, scard.SCARD_LEAVE_CARD))

        # reader available again
        (res, card, prot) = self.reader.Connect(scard.SCARD_SHARE_SHARED,
                                                scard.SCARD_PROTOCOL_T1)
        self.assertEquals(scard.SCARD_S_SUCCESS, res)
        self.assertEquals(scard.SCARD_S_SUCCESS,
                         self.reader.Disconnect(card, scard.SCARD_LEAVE_CARD))

    def testReconnect(self):
        (res, card, prot) = self.reader.Connect(scard.SCARD_SHARE_SHARED,
                                                scard.SCARD_PROTOCOL_T1)
        self.assertEquals(scard.SCARD_S_SUCCESS, res)
        self.assertEquals(scard.SCARD_E_INVALID_HANDLE,
                          self.reader.Reconnect(2*card, scard.SCARD_SHARE_SHARED,
                                                scard.SCARD_PROTOCOL_T1,
                                                scard.SCARD_LEAVE_CARD)[0])
        (res, prot) = self.reader.Reconnect(card, scard.SCARD_SHARE_SHARED,
                                            scard.SCARD_PROTOCOL_T1,
                                            scard.SCARD_LEAVE_CARD)
        self.assertEquals(scard.SCARD_S_SUCCESS, res)
        (res, prot) = self.reader.Reconnect(card, scard.SCARD_SHARE_EXCLUSIVE,
                                            scard.SCARD_PROTOCOL_T1,
                                            scard.SCARD_LEAVE_CARD)
        self.assertEquals(scard.SCARD_S_SUCCESS, res)
        (res, prot) = self.reader.Reconnect(card, scard.SCARD_SHARE_SHARED,
                                            scard.SCARD_PROTOCOL_T1,
                                            scard.SCARD_LEAVE_CARD)
        self.assertEquals(scard.SCARD_S_SUCCESS, res)
        self.assertEquals(scard.SCARD_S_SUCCESS,
                          self.reader.Disconnect(card, scard.SCARD_LEAVE_CARD))

    def testTransactionsOneThread(self):
        (res, card, prot) = self.reader.Connect(scard.SCARD_SHARE_SHARED,
                                                scard.SCARD_PROTOCOL_T1)
        self.assertEquals(scard.SCARD_S_SUCCESS, res)

        self.assertEquals(scard.SCARD_E_NOT_TRANSACTED,
                          self.reader.EndTransaction(card,
                                                     scard.SCARD_LEAVE_CARD))
        self.assertEquals(scard.SCARD_S_SUCCESS,
                          self.reader.BeginTransaction(card))
        self.assertEquals(scard.SCARD_S_SUCCESS,
                          self.reader.EndTransaction(card,
                                                     scard.SCARD_LEAVE_CARD))

        self.assertEquals(scard.SCARD_S_SUCCESS,
                          self.reader.BeginTransaction(card))
        self.assertEquals(scard.SCARD_S_SUCCESS,
                          self.reader.BeginTransaction(card))
        self.assertEquals(scard.SCARD_S_SUCCESS,
                          self.reader.EndTransaction(card,
                                                     scard.SCARD_LEAVE_CARD))
        self.assertEquals(scard.SCARD_S_SUCCESS,
                          self.reader.EndTransaction(card,
                                                     scard.SCARD_LEAVE_CARD))
        self.assertEquals(scard.SCARD_E_NOT_TRANSACTED,
                          self.reader.EndTransaction(card,
                                                     scard.SCARD_LEAVE_CARD))
        self.assertEquals(scard.SCARD_S_SUCCESS,
                          self.reader.BeginTransaction(card))
        (res, prot) = self.reader.Reconnect(card, scard.SCARD_SHARE_SHARED,
                                            scard.SCARD_PROTOCOL_T1,
                                            scard.SCARD_LEAVE_CARD)
        self.assertEquals(scard.SCARD_S_SUCCESS, res)
        self.assertEquals(scard.SCARD_S_SUCCESS,
                          self.reader.BeginTransaction(card))
        self.assertEquals(scard.SCARD_S_SUCCESS,
                          self.reader.EndTransaction(card,
                                                     scard.SCARD_LEAVE_CARD))
        self.assertEquals(scard.SCARD_E_NOT_TRANSACTED,
                          self.reader.EndTransaction(card,
                                                     scard.SCARD_LEAVE_CARD))

        self.assertEquals(scard.SCARD_S_SUCCESS,
                          self.reader.Disconnect(card, scard.SCARD_LEAVE_CARD))
        

    def testFlagFunc(self):
        self.assertTrue(flag_set(1, 3))
        self.assertFalse(flag_set(1, 2))
