import pybonjour
import select

from webscard.utils import application

name = "WebSCard"
regtype = ["http", "smartcard"]

sdRef = []

def _register_callback(sdRef, flags, errorCode, name, regtype, domain):
    if errorCode == pybonjour.kDNSServiceErr_NoError:
        print 'Registered service: %s' % regtype
    else:
        print "Error while registrating : %d" % errorCode

def register(port):
    for i in range(len(regtype)):
        sdRef.append(pybonjour.DNSServiceRegister(
                name = name,
                regtype = "_%s._tcp" % regtype[i],
                port = port,
                callBack = _register_callback))

        ready, _dummy1, _dummy2 = select.select([sdRef[i]], [], [])
        if sdRef[i] in ready:
            pybonjour.DNSServiceProcessResult(sdRef[i])

# Hmm, that one is tricky as anyway, they get cleaned by the garbage collector ...
def finalize():
    for conn in sdRef:
        conn.close()
