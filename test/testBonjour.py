import unittest, time

import Zeroconf

from webscard import bonjour

class testBonjour(unittest.TestCase):

    def setUp(self):
        bonjour.register(333, ["impl1", "impl2", "impl3", "impl4"])

    def tearDown(self):
        bonjour.finalize()

    def testHTTP(self):
        class MyListener(object):
            def __init__(self):
                self.found = {}

            def removeService(self, server, type, name):
                if repr(name) in self.found:
                    del self.found[repr(name)]

            def addService(self, server, type, name):
                self.found[repr(name)] = server.getServiceInfo(type, name)

        server = Zeroconf.Zeroconf()
        listener = MyListener()
        browser = Zeroconf.ServiceBrowser(server, "_http._tcp.local.", listener)
        time.sleep(3)
        server.close()

        found = False
        for value in listener.found.values():
            name = value.name[:value.name.index('.')]
            if name.startswith("WebSCard"):
                found = True
                self.assertEquals(333, value.port)
                self.assertEquals('1', value.properties['txtvers'])
                self.assert_("impl1" in value.properties)
                self.assert_("impl2" in value.properties)
                self.assert_("impl3" in value.properties)
                self.assert_("impl4" in value.properties)
                self.assertEquals('1', value.properties['protovers'])
        self.assertTrue(found)

    def testSC_HTTP(self):
        class MyListener(object):
            def __init__(self):
                self.found = {}

            def removeService(self, server, type, name):
                if repr(name) in self.found:
                    del self.found[repr(name)]

            def addService(self, server, type, name):
                self.found[repr(name)] = server.getServiceInfo(type, name)

        server = Zeroconf.Zeroconf()
        listener = MyListener()
        browser = Zeroconf.ServiceBrowser(server, "_smartcard-http._tcp.local.", listener)
        time.sleep(5)
        server.close()

        found = False
        for value in listener.found.values():
            name = value.name[:value.name.index('.')]
            if name.startswith("WebSCard"):
                found = True
                self.assertEquals(333, value.port)
                self.assertEquals('1', value.properties['txtvers'])
                self.assert_("impl1" in value.properties)
                self.assert_("impl2" in value.properties)
                self.assert_("impl3" in value.properties)
                self.assert_("impl4" in value.properties)
                self.assertEquals('1', value.properties['protovers'])
        self.assertTrue(found)
