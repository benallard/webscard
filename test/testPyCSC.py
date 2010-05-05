import unittest

from smartcard import scard

from webscard.implementations import pycsc

from webscard import config

class testPyCSC(unittest.TestCase):

    def setUp(self):
        cfg = config.Config([])
        cfg.add_section('pycsc')
        cfg.set('pycsc', 'ATR', '3B 00 00')
        self.pycsc = pycsc.PyCSC("pycsc", cfg)

    def testContexts(self):
        self.assertEquals(scard.SCARD_E_INVALID_HANDLE,
                          self.pycsc.SCardReleaseContext(56))
        (res, context) = self.pycsc.SCardEstablishContext(scard.SCARD_SCOPE_USER)
        self.assertEquals(scard.SCARD_S_SUCCESS, res)
        self.assertEquals(scard.SCARD_S_SUCCESS,
                          self.pycsc.SCardReleaseContext(context))
        self.assertEquals(scard.SCARD_E_INVALID_HANDLE,
                          self.pycsc.SCardReleaseContext(context))
