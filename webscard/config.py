import yaml
import random

LETTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

class Config(dict):
    def __init__(self, file=''):
        self.defaultvalues()
        f = open(file, 'r')
        self.update(yaml.load(f.read()))
        f.close()
        self.addhardcodedvalues()
        self.port = None
        self.defaultsecret = "".join([random.choice(LETTERS)
                                      for i in range(20)])

    def defaultvalues(self):
        self.update({
            'cookies': {},
            'web': {},
            'logger': {},
            'internal': {}
        })

    def addhardcodedvalues(self):
        """ Those are constant values, not default ones """
        self.update({
            'pyscard': {'module': 'smartcard.scard', 'hard': True},
            'clusterscard': {
                'module': 'webscard.implementations.clusterscard',
                'hard': True,
                'free': 'isfree',
                'acquire': 'acquire',
                'release': 'release',},
            'pycsc': {
                'module': 'webscard.implementations.pycsc',
                'classname': 'PyCSC',},
            'empty': {
                'module': 'webscard.implementations.empty',
                'classname': 'Empty',},
        })

    # And finally, functions that really make sense in our context
    def getimplementations(self):
        """ Return a list of the implementations in the current server """
        return self['internal'].get('implementations', ['pyscard'])

    def gethost(self):
        """ The interface where the server is published """
        return self['web'].get('host', '0.0.0.0')

    def getport(self):
        """
        Port on which we runs
        It is interesting to set it random if we have Bonjour enabled.
        """
        if self.port is not None:
            return self.port
        if self['web'].get('randomport', False):
            # Let's pray the port will indeed be free ...
            self.port = random.randint(49152, 65535)
        else:
            self.port = self['web'].get('port', 3333)
        return self.port

    def getcookiesecret(self):
        """ Secret key that secure the sessions inside the cookies """
        return self['cookies'].get('secret', self.defaultsecret)
