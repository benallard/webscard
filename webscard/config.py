import yaml
import random

LETTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

class RecursiveDictionary(dict):
    """ taken from https://gist.github.com/114831
    RecursiveDictionary provides the methods rec_update and iter_rec_update
    that can be used to update member dictionaries rather than overwriting
    them."""
    __author__ = 'jannis@itisme.org (Jannis Andrija Schnitzer)'
    def rec_update(self, other, **third):
        """Recursively update the dictionary with the contents of other and
        third like dict.update() does - but don't overwrite sub-dictionaries.

        Example:
        >>> d = RecursiveDictionary({'foo': {'bar': 42}})
        >>> d.rec_update({'foo': {'baz': 36}})
        >>> d
        {'foo': {'baz': 36, 'bar': 42}}
        """
        try:
            iterator = other.iteritems()
        except AttributeError:
            iterator = other
        self.iter_rec_update(iterator)
        self.iter_rec_update(third.iteritems())

    def iter_rec_update(self, iterator):
        for (key, value) in iterator:
            if key in self and \
               isinstance(self[key], dict) and isinstance(value, dict):
                self[key] = RecursiveDictionary(self[key])
                self[key].rec_update(value)
            else:
                self[key] = value

class Config(RecursiveDictionary):
    def __init__(self, file=''):
        self.defaultvalues()
        f = open(file, 'r')
        data = f.read()
        f.close()
        try:
            config = yaml.load(data)
        except yaml.parser.ParserError, e:
            config = {}
            print "Error parsing configuration file %s" % file
            print e
        self.rec_update(config)
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
        self.rec_update({
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
