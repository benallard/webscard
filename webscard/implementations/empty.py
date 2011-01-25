
from smartcard import scard as pyscard
from smartcard.scard import SCARD_E_NO_SERVICE

class Empty(object):
    """
    creating a class allows me to use the __getattr__ trick.
    """

    def __init__(self, name, config):
        pass

    def SCardEstablishContext(self, dwScope):
        """
        No valid context means no continuation
        """
        return SCARD_E_NO_SERVICE, 0

    # For all the other functions
    def __getattr__(self, name):
        return getattr(pyscard, name)
