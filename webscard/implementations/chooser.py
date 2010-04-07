from webscard.utils import application

from webscard.implementations.pyscard import Implementation

TIMEOUT = 5 * 60 # 5 min.

class Chooser(object):
    pool = []
    map = {}
    def __init__(self):
        cfg = application.config
        impls = cfg.getstring('internal.implementations', 'pyscard')
        impls = impls.split()
        for implname in impls:
            impl = self.create(implname)
            if impl is not None:
                self.pool.append(impl)

    def create(self, name):
        cfg = application.config
        module = cfg.getstring('%s.module' % name, None)
        if module is None:
            if name == 'pyscard':
                module = 'smartcard.scard'
            else:
                raise ValueError('%s.module config option missing' % name)
        classname = cfg.getstring('%s.classname' % name, None)
        mod = __import__(module, globals(), locals(), [''])
        print "mod is %s" % mod
        if classname is None:
            impl = mod
        else:
            try:
                impl = getattr(mod, classname)()
            except AttributeError:
                raise AttributeError("class %s does not exist on the specified module" % classname)
        return impl

    # Actually, from those three functions, `get` is enough ...

    def getone(self, session):
        return self.pool[0]

    def setimpl(self, session, implementation):
        self.map[session.uid] = implementation

    def getimpl(self, session):
        return self.pool[0]

