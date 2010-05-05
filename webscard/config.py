from ConfigParser import SafeConfigParser, NoOptionError, NoSectionError
from ConfigParser import DuplicateSectionError

import random

LETTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

class Config(SafeConfigParser):
    def __init__(self, file):
        SafeConfigParser.__init__(self)
        self.read(file)
        self.addhardcodedvalues()
        self.port = None
        self.defaultsecret = "".join([random.choice(LETTERS)
                                      for i in range(20)])

    def addhardcodedvalues(self):
        """ Those are not for default values, but for constant values """
        try:
            self.add_section('web')
        except DuplicateSectionError:
            pass

        try:
            self.add_section('pyscard')
        except DuplicateSectionError:
            pass
        self.set('pyscard', 'module', 'smartcard.scard')
        self.set('pyscard', 'hard', "yes")

        try:
            self.add_section('clusterscard')
        except DuplicateSectionError:
            pass
        self.set('clusterscard', 'module',
                 'webscard.implementations.clusterscard')
        self.set('clusterscard', 'hard', "yes")
        self.set('clusterscard', 'free', 'isfree')
        self.set('clusterscard', 'acquire', 'acquire')
        self.set('clusterscard', 'release', 'release')

    def getstring(self, item, default=""):
        section, option = item.split('.')
        try:
            val = self.get(section, option, 1)
        except (NoSectionError, NoOptionError):
            val = default
        return val

    def getbool(self, item, default=False):
        section, option = item.split('.')
        try:
            val = self.getboolean(section, option)
        except (NoSectionError, NoOptionError):
            val = default
        return val

    def getinteger(self, item, default=0):
        section, option = item.split('.')
        try:
            val = self.getint(section, option)
        except (NoSectionError, NoOptionError):
            val = default
        return val

    # And finally, functions that really make sense in our context
    def getimplementations(self):
        """ Return a list of the implementations in the current server """
        impls = self.getstring('internal.implementations', 'pyscard')
        return impls.split()

    def gethost(self):
        """ The interface where the server is published """
        return self.getstring('web.host', '0.0.0.0')

    def getport(self):
        """
        Port on which we runs
        It is interesting to set it random if we have Bonjour enabled.
        """
        if self.port is not None:
            return self.port
        if self.getbool('web.randomport', False):
            # Let's pray the port will indeed be free ...
            self.port = random.randint(49152, 65535)
        else:
            self.port = self.getinteger('web.port', 3333)
        return self.port

    def getcookiesecret(self):
        """ Secret key that secure the sessions inside the cookies """
        return self.getstring('cookies.secret',
                              self.defaultsecret)
