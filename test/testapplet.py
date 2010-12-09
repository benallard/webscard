from pythoncard import framework

class MyApplet(framework.Applet):
    AID = framework.AID([0xa0, 0x00, 0x00, 0x00, 0x00], 0, 5)
    @staticmethod
    def install(bArray, bOffset, bLength):
        MyApplet().register()

    def process(self, apdu):
        if self.selectingApplet():
            return

        raise framework.ISOException(0x6ABC)
