"""
This is a Python token, it reprsents a Token + the CardManager

"""

from pythoncard.framework import Applet, ISO7816, ISOException, APDU

from webscard.utils import loadpath

def swtotransmitres(sw):
    sw1 = sw // 256
    sw2 = sw % 256
    return 0, [sw1, sw2]

class Token(object):
    def __init__(self, name, config):
        ATR = config.getstring("%s.ATR" % name, "3B 00")
        ATR = ATR.split()
        self.ATR = map(lambda x: int(x, 16), ATR)
        self.applets = {}

        def defineMyregister(applets):
            """
            This uses a closure to pass the local `applets` to the Applet
            register function
            """
            def myregister(self, bArray = [], bOffset=0, bLength=0):
                if bLength != 0:
                    aid = AID(bArray, bOffset, bLength)
                else:
                    aid = self.AID
                applets[aid] = self
            return myregister
        Applet.register = defineMyregister(self.applets)

        # First, we load all the applet modules
        applets = config.getstring('%s.applets' % name)
        applets = applets.split()
        for applet in applets:
            modulepath = config.getstring("%s.%s"  % (name,applet), None)
            loadpath(modulepath, "%s.%s" % (name, applet))
            # Then we instanciate all the applets in the module we just loaded
            for applet in Applet.__subclasses__():
                if applet.__module__.startswith(name + "_"):
                    # What about registering the same applet with different AIDs
                    # or with install parameters
                    applet.install([0,0,0], 0, 3)
        # currently selected Applet
        self.selected = None

    def power(self):
        pass

    def unpower(self):
        if self.selected is not None:
            self.selected.deselect()
        self.selected = None

    def _cmprocess(self, bytes):
        """
        the `process` command of the Card Manager.
        It can handle for now only SELECT
        """
        if (bytes[0] & 0x80) == 0x00:
            # We should maybe be more strict on the select Applet APDU
            if bytes[1:3] == [ISO7816.INS_SELECT, 0x04]:
                self._cmselect(bytes)

    def _cmselect(self, bytes):
        """ Select According to the Card Manager """
        potential = None
        threshold = bytes[ISO7816.OFFSET_LC]
        while (potential == None) and (threshold > 4):
            for aid in self.applets:
                if aid.equals(bytes, ISO7816.OFFSET_CDATA,
                              min(bytes[ISO7816.OFFSET_LC], threshold)):
                    potential = self.applets[aid]
            threshold -= 1

        if potential is None:
            raise ISOException(ISO7816.SW_FILE_NOT_FOUND)
        if self.selected is not None:
            self.selected.deselect()
            self.selected = None
        if potential.select():
            potential._selectingApplet = True
            self.selected = potential

    def transmit(self, bytes):
        try:
            # manage the applet selection
            if self.selected is not None:
                self.selected._selectingApplet = False
            self._cmprocess(bytes)
            if self.selected is None:
                raise ISOException(ISO7816.SW_APPLET_SELECT_FAILED)
            apdu = APDU(bytes)
            self.selected.process(apdu)
        except ISOException, isoe:
            return swtotransmitres(isoe.getReason())
        except Exception, e:
            # This is to avoid throwing Exception to the web interface
            return swtotransmitres(ISO7816.SW_UNKNOWN)
            #return scard.SCARD_F_INTERNAL_ERROR, []
        
        buf = apdu._APDU__buffer[:apdu._outgoinglength]
        buf.extend([0x90, 0x00])
        return 0, buf
