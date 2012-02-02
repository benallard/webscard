"""
This is a Python token, it reprsents a Token + the CardManager

"""

from pythoncard.framework import Applet, ISO7816, ISOException, APDU, JCSystem, AID

try:
    from caprunner import resolver, capfile
    from caprunner.utils import d2a, a2d
    from caprunner.interpreter import JavaCardVM, ExecutionDone
    from caprunner.interpreter.methods import JavaCardStaticMethod, JavaCardVirtualMethod, NoSuchMethod
    CAPRunner = True
except ImportError:
    CAPRunner = False

try:
    from virtualsmartcard import VirtualSmartcard
    vsmartcard = True
except ImportError:
    vsmartcard = False

from webscard.utils import loadpath

def swtotransmitres(sw):
    sw1 = (sw >> 8) & 0xff
    sw2 = sw & 0xff
    return 0, [sw1, sw2]

class Token(object):
    """ This is a generic Token """

    def __init__(self, name, config):
        ATR = config.get('ATR', "3B 00")
        ATR = ATR.split()
        self.ATR = map(lambda x: int(x, 16), ATR)

    def power(self):
        pass

    def unpower(self):
        pass

    @staticmethod
    def get(name, config):
        """ This returns or a PyToken or a CAPToken """
        if 'CAPFile' in config:
            if not CAPRunner:
                # There should be a better way to ... 
                return None
            return CAPToken(name, config)
        elif 'applets' in config:
            return PyToken(name, config)
        elif 'vsmartcard' in config:
            if not vsmartcard:
                # idem
                print "no vsmartcard"
                return None
            return VToken(name, config)
        else:
            print "None of CAPFile, applets, or vsmartcard"

class PyToken(Token):
    """ 
    This is a python token: the Applet is written in python.
    """
    def __init__(self, name, config):
        Token.__init__(self, name, config)
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
        applets = config.get('applets', [])
        for applet in applets:
            modulepath = config.get(applet)
            loadpath(modulepath, "%s.%s" % (name, applet))
            # Then we instanciate all the applets in the module we just loaded
            for applet in Applet.__subclasses__():
                if applet.__module__.startswith(name + "_"):
                    # What about registering the same applet with different AIDs
                    # or with install parameters
                    applet.install([0,0,0], 0, 3)
        # currently selected Applet
        self.selected = None

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

class CAPToken(Token):
    """
    This token is a Java Token. 
    The Applet is actually a capfile. The code below is taken from runcap.py
    """
    def __init__(self, name, config):
        Token.__init__(self, name, config)

        self.current_install_aid = None
        # a2d(aid) => Applet
        self.applets = {}
        # channel => Applet
        self.selected = [None, None, None, None]
        # opened
        self.channels = [True, False, False, False]
        # current one
        self.current_channel = 0

        self.installJCFunctions()

        self.capfilename = config.get("capfile")
        # Create the VM
        self.vm = JavaCardVM(resolver.linkResolver())
        # Load the CAP File
        self.vm.load(capfile.CAPFile(self.capfilename))        

    def installJCFunctions(self):
        """ This tweak the JC Framework to make it fit our environment """

        def defineMyregister(self):
            """
            This uses a closure to pass the local `self` to the Applet
            register function
            """
            def myregister(applet, bArray = [], bOffset=0, bLength=0):
                if bLength != 0:
                    aid = AID(bArray, bOffset, bLength)
                else:
                    aid = self.current_install_aid
                self.applets[a2d(aid.aid)] = applet
            return myregister
        Applet.register = defineMyregister(self)

        def defineMylookupAID(applets):
            def mylookupAID(buffer, offset, length):
                if a2d(buffer[offset:offset + length]) in applets:
                    return AID(buffer, offset, length)
                return None
            return mylookupAID
        JCSystem.lookupAID = defineMylookupAID(self.applets)

        def defineMyisAppletActive(selected):
            def myisAppletActive(aid):
                return applets[a2d(aid.aid)] in selected
            return myisAppletActive
        JCSystem.isAppletActive = defineMyisAppletActive(self.selected)

        def defineMygetAssignedChannel(self):
            def mygetAssignedChannel():
                return self.current_channel
        JCSystem.getAssignedChannel = defineMygetAssignedChannel(self)


    def unpower(self):
        for i in range(len(self.selected)):
            apl = self.selected[i]
            if apl is not None:
                apl._cmdeselect(i)

    def transmit(self, bytes):
        self.vm.log = ""
        self.current_channel = bytes[0] & 0x3
        if self.selected[self.current_channel]:
            self.selected[self.current_channel]._selectingApplet = False
        if not bool(bytes[0] & 0x80):
            # ISO command
            if bytes[1:4] == [-92, 4, 0]:
                aid = bytes[5:5 + bytes[4]]
                # select command A4 04 00
                self._cmselect(aid)
            elif bytes[1:4] == [112, 0, 0]:
                # open channel : 70 00 00
                for idx in xrange(4):
                    if not self.channels[idx]:
                        self.channels[idx] = True
                        buf = [idx]
                        buf.extend(d2a('\x90\x00'))
                        return 0, buf
                return 0, swtotransmitres(ISO7816.SW_WRONG_P1P2)
            elif bytes[1:3] == [112, -128]:
                # close channel: 70 80
                if self.channels[self.current_channel]:
                    self.channels[self.current_channel] = False
                    buf = d2a('\x90\x00')
                    return 0, buf
                return swtotransmitres(ISO7816.SW_WRONG_P1P2)
            elif bytes[1:4] == [-26, 12, 0]:
                # install : E6 0C 00
                self.install(bytes, 5)

        # Make an APDU object
        apdu = APDU(bytes)
        # pass to the process method
        applet = self.selected[self.current_channel]
        if applet is None:
            return swtotransmitres(ISO7816.SW_FILE_NOT_FOUND)
        self.vm.frame.push(applet)
        self.vm.frame.push(apdu)
        # invoke the process method
        self.vm._invokevirtualjava(JavaCardVirtualMethod(
                applet._ref.offset,
                7, # process
                False,
                self.vm.cap_file,
                self.vm.resolver))
        try:
            while True:
                self.vm.step()
        except ExecutionDone:
            pass
        except ISOException, isoe:
            return swtotransmitres(isoe.getReason())
        except Exception, e:
            return swtotransmitres(ISO7816.SW_UNKNOWN)
        buf = apdu._APDU__buffer[:apdu._outgoinglength]
        buf.extend(d2a('\x90\x00'))
        return 0, buf


    def _cmselect(self, aid):
        channel = self.current_channel
        # We should spend some time looking for an applet there ...
        potential = self.applets[a2d(aid)]
        applet = self.selected[channel]
        if applet is not None:
            if not self._cmdeselect(channel):
                return False
            self.selected[channel] = None

        self.vm.frame.push(potential)
        try:
            selectmtd = JavaCardVirtualMethod(potential._ref.offset, 6, False, vm.cap_file, vm.resolver)
        except NoSuchMethod:
            selected[channel] = potential
            selected[channel]._selectingApplet = True
            return True
        self.vm._invokevirtualjava(selectmtd)
        try:
            while True:
                vm.step()
        except ExecutionDone:
            pass
        if self.vm.frame.getValue() == True:
            self.selected[channel] = potential
            self.selected[channel]._selectingApplet = True
            return True
        else:
            return False

    def _cmdeselect(self, channel):
        applet = self.selected[channel]
        self.vm.frame.push(applet)
        try:
            deselectmtf = JavaCardVirtualMethod(applet._ref.offset, 4, False, vm.cap_file, vm.resolver)
        except NoSuchMethod:
            self.selected[channel] = None
            return True
        self.vm._invokevirtualjava(deselectmtd)
        try:
            while True:
                vm.step()
        except ExecutionDone:
            pass
        if vm.frame.getValue():
            self.selected[channel] = None
            return True
        return False


    def install(self, data, offset):
        """ 
        data[offset:] is len||appletaid||len||installdata
        where installdata is the data given to the install method
        """
        aidlen = data[offset]
        offset += 1
        aid = data[offset: offset + aidlen]
        offset += aidlen
        length = data[offset]
        offset += 1
        # data[offset:offset+length] is what is given to the install JavaCard 
        # method which means: len-instanceaid-len-stuff-len-customparams
        # where instance AID might be empty
        self.vm.frame.push(data)
        self.vm.frame.push(offset)
        self.vm.frame.push(length)
        applet = None
        for apl in self.vm.cap_file.Applet.applets:
            if a2d(aid) == a2d(apl.aid):
                applet = apl
            break
        if applet is None:
            return
        self.current_install_aid = aid
        self.vm._invokestaticjava(JavaCardStaticMethod(
                applet.install_method_offset,
                vm.cap_file,
                vm.resolver))
        try:
            while True:
                vm.step()
        except ISOException, ie:
            return swtotransmitres(ie.getReason())
        except ExecutionDone:
            pass
        self.current_install_aid = None
        return swtotransmitres(ISO7816.SW_NO_ERROR)

class VToken(Token):
    def __init__(self, name, config):
        if config['vsmartcard'] not in ('NPAOS', 'RelayOS',
                                        'CryptoflexOS', 'Iso7816OS'):
            return

        cls = getattr(VirtualSmartcard, config['vsmartcard'])
        self.vSC = cls(**config['initparams'])
        self.ATR = self.vSC.atr

    def power(self):
        self.vSC.powerUp()

    def unpower(self):
        self.vSC.powerDown()

    def transmit(self, bytes):
        msg = "".join([chr(b) for b in bytes])
        rapdu = self.vSC.execute(msg)
        return 0, list(bytes(rapdu))
