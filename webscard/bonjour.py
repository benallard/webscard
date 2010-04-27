"""
Publishing the service via Bonjour (ZeroConf))
"""

try:
    import pybonjour
except: # WindowsError on Windows
    pybonjour = None

NAME = "WebSCard"
REGTYPE = [
    "http", # Our HTTP interface
    "smartcard-http", # SmartCard via HTTP
]

REFS = []

def _register_callback(sdRef, flags, errorCode, name, regtype, domain):
    if errorCode == pybonjour.kDNSServiceErr_NoError:
        print 'Registered service: %s' % regtype
    else:
        print "Error while registrating : %d" % errorCode

ns = lambda s: "%c%s" % (len(s), s)

def register(port, implementations):
    if pybonjour == None:
        return
    txt = ns("txtvers=1")
    txt += ns("protovers=1")
    for imp in implementations:
        txt += ns(imp)
    for i in range(len(REGTYPE)):
        REFS.append(pybonjour.DNSServiceRegister(
                name = NAME,
                regtype = "_%s._tcp" % REGTYPE[i],
                port = port,
                callBack = _register_callback,
                txtRecord = txt))

        pybonjour.DNSServiceProcessResult(REFS[i])

def finalize():
    """
    That one is tricky as anyway,
    They get cleaned by the garbage collector ...
    """
    for conn in REFS:
        conn.close()
