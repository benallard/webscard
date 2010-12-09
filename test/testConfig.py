import unittest

from webscard.config import Config

class testConfig(unittest.TestCase):    

    def testDefaults(self):
        cfg = Config()

        self.assertEquals("",
                          cfg.getstring("foo.bar"))
        self.assertEquals(False,
                          cfg.getbool("bar.baz"))
        self.assertEquals(0,
                          cfg.getinteger("foo.baz"))

    def testNetworkParams(self):
        cfg = Config()

        self.assertEquals("0.0.0.0", 
                          cfg.gethost())
        self.assertEquals(3333, cfg.getport())

        del cfg
        cfg = Config()
        cfg.set("web", "randomport", "True")

        port = cfg.getport()
        self.assertEquals(port, cfg.getport())

        del cfg
        cfg = Config()
        cfg.set("web", "randomport", "True")
        self.assertFalse(port == cfg.getport())
        
    def testCookieSecret(self):
        cfg = Config()
        cfg.add_section("cookies")
        cfg.set('cookies', 'secret', "ULTRA SECRET")
        self.assertEquals("ULTRA SECRET",
                          cfg.getcookiesecret())

        del cfg
        cfg = Config()
        secret = cfg.getcookiesecret()
        self.assertEquals(secret, cfg.getcookiesecret())

        del cfg
        cfg = Config()
        self.assertFalse(secret == cfg.getcookiesecret())
