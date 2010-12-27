"""
Publishing the service via Bonjour (ZeroConf))
"""

import socket

NAME = "WebSCard (%s)" % socket.gethostname().split('.')[0]
REGTYPE = [
    "http", # Our HTTP interface
    "smartcard-http", # SmartCard via HTTP
]

try:
    from webscard.bonjour import pybj
    register = pybj.register
    finalize = pybj.finalize
except: # WindowsError on Windows
    print "Using Python pure Zeroconf implementation"
    from webscard.bonjour import zc
    register = zc.register
    finalize = zc.finalize

