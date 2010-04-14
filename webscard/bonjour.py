import pybonjour
import select

from webscard.utils import application

name = "WebSCard"
regtype = [
    "http", # Our HTTP interface
    "smartcard-http", # SmartCard via HTTP
]

sdRef = []

def _register_callback(sdRef, flags, errorCode, name, regtype, domain):
    if errorCode == pybonjour.kDNSServiceErr_NoError:
        print 'Registered service: %s' % regtype
    else:
        print "Error while registrating : %d" % errorCode

ns = lambda s: "%c%s" % (len(s), s)

def register(port, implementations):
    txt = ns("txtvers=1")
    txt += ns("protovers=1")
    for imp in implementations:
        txt += ns(imp)
    for i in range(len(regtype)):
        sdRef.append(pybonjour.DNSServiceRegister(
                name = name,
                regtype = "_%s._tcp" % regtype[i],
                port = port,
                callBack = _register_callback,
                txtRecord = txt))

        pybonjour.DNSServiceProcessResult(sdRef[i])

# Hmm, that one is tricky as anyway, they get cleaned by the garbage collector ...
def finalize():
    for conn in sdRef:
        conn.close()
