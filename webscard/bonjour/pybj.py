import pybonjour

from webscard.bonjour import REGTYPE, NAME

PYBJ_REFS = []

def _register_callback(sdRef, flags, errorCode, name, regtype, domain):
    pass


def register(port, implementations):
    ns = lambda s: "%c%s" % (len(s), s)
    txt = ns("txtvers=1")
    txt += ns("protovers=1")
    for imp in implementations:
        txt += ns("%s=true" % imp)
    for i in range(len(REGTYPE)):
        sdRef = pybonjour.DNSServiceRegister(
                name = NAME,
                regtype = "_%s._tcp" % REGTYPE[i],
                port = port,
                callBack = _register_callback,
                txtRecord = txt)

        pybonjour.DNSServiceProcessResult(sdRef)

        PYBJ_REFS.append(sdRef)

def finalize():
    """
    That one is tricky as anyway,
    They get cleaned by the garbage collector ...
    """
    for conn in PYBJ_REFS:
        PYBJ_REFS.remove(conn)
        conn.close()
