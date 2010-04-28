import unittest

from webscard.implementations.happy import Happy

READERNAME = "Happy Reader 0"

class testHappy(unittest.TestCase):

    def setUp(self):
        self.hap = Happy('happy', None)

    def tearDown(self):
        del self.hap

    def testOk(self):
        self.assertEquals((0, 0),
                          self.hap.SCardEstablishContext(2))
        self.assertEquals((0, [READERNAME]),
                          self.hap.SCardListReaders(0, []))
        self.assertEquals((0, 0, 2),
                          self.hap.SCardConnect(0,READERNAME,2, 3))
        self.assertEquals((0, READERNAME, 52, 2, [0x3b, 0x00]),
                          self.hap.SCardStatus(0))
        self.assertEquals((0, [0x90, 0x00]),
                          self.hap.SCardTransmit(0, 2, [0x00, 0x00]))
        self.assertEquals(0,
                          self.hap.SCardDisconnect(0,0))
        self.assertEquals(0,
                          self.hap.SCardReleaseContext(0))
