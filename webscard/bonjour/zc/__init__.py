from webscard.bonjour import Zeroconf
import socket

from webscard.bonjour import REGTYPE, NAME

ZC_SERVER = []


def _getip():
    # finds external-facing interface without sending any packets (Linux)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('1.0.0.1', 0))
        ip = s.getsockname()[0]
        return ip
    except:
        pass

    # Generic method, sometimes gives useless results
    try:
        dumbip = socket.gethostbyaddr(socket.gethostname())[2][0]
        if not dumbip.startswith('127.') and ':' not in dumbip:
            return dumbip
    except socket.gaierror:
        dumbip = '127.0.0.1'

    # works elsewhere, but actually sends a packet
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('1.0.0.1', 1))
        ip = s.getsockname()[0]
        return ip
    except:
        pass

    return dumbip

def register(port, implementations):
    ip = _getip()

    server = Zeroconf.Zeroconf(ip)
    
    # Get local IP address
    local_ip = socket.inet_aton(ip)

    hostname = socket.gethostname().split('.')[0]
    host = hostname + ".local"

    props = {'txtvers':"1","protovers":"1"}
    for impl in implementations:
        props[impl] = 1

    for regtype in REGTYPE:
        svc = Zeroconf.ServiceInfo(type = "_%s._tcp.local." % regtype,
                                   name = "%s._%s._tcp.local." % (NAME, regtype),
                                   server = host,
                                   address = local_ip,
                                   port = port,
                                   weight = 0, priority=0,
                                   properties = props,
                                   )
        server.registerService(svc)
    
    ZC_SERVER.append(server)
    

def finalize():
    if len(ZC_SERVER) > 0:
        ZC_SERVER.pop().close()
