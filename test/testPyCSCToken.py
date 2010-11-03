import unittest, os

from webscard.config import Config

from webscard.implementations.pycsc.token import Token

from pythoncard.framework import ISO7816, ISOException


class testPyCSCToken(unittest.TestCase):

    def _testConfig(self):
        cfg = Config()
        cfg.add_section('pycsc')
        cfg.set('pycsc', 'ATR', "3B 00")
        cfg.set('pycsc', 'applets', 'testapplet')
        appletfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), "testapplet.py")
        cfg.set('pycsc', 'testapplet', appletfile)
        return cfg

    def testLoader(self):
        tkn = Token('pycsc', self._testConfig())

        #Finally, check that our applet is registered !
        self.assertEquals(1, len(tkn.applets))
        aid = tkn.applets.keys()[0]
        self.assert_(aid.equals([0xa0, 0,0,0,0], 0, 5))

    def testSelect(self):
        tkn = Token('pycsc', self._testConfig())

        self.assertEquals(None, tkn.selected)

        tkn._cmselect([0,0,0,0,5, 0xa0, 0,0,0,0])
        self.assertEquals(tkn.applets[tkn.applets.keys()[0]], tkn.selected)

        try:
            tkn._cmselect([0,0,0,0,5, 0xa0, 0,9,0,0])
            self.fail()
        except ISOException, ie:
            self.assertEquals(ISO7816.SW_FILE_NOT_FOUND, ie.getReason())
        self.assertEquals(tkn.applets[tkn.applets.keys()[0]], tkn.selected)

        tkn.unpower()
        self.assertEquals(None, tkn.selected)

        tkn._cmselect([0,0,0,0,8, 0xa0, 0,0,0,0, 8, 7, 2])
        self.assertEquals(tkn.applets[tkn.applets.keys()[0]], tkn.selected)

    def testSelectViaTransmit(self):
        tkn = Token('pycsc', self._testConfig())
        self.assertEquals(None, tkn.selected)

        hresult, response = tkn.transmit([0,0xA4,0,0,5, 0xa0, 0,0,0,0])
        self.assertEquals(0, hresult)
        self.assertEquals([0x90, 0x00], response)
        self.assertEquals(tkn.applets[tkn.applets.keys()[0]], tkn.selected)

        hresult, response = tkn.transmit([0,0xA4,0,0,5, 0xa0, 0,0,9,0])
        self.assertEquals(0, hresult)
        self.assertEquals([0x6A, 0x82], response) # No such File

        self.assertEquals(tkn.applets[tkn.applets.keys()[0]], tkn.selected)
