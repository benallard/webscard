import imp, os, random

from webscard.utils import application

from webscard.implementations.pyscard import Implementation

TIMEOUT = 5 * 60 # 5 min.

class Implementation(object):
    
    def __init__(self, name):
        self.name = name
        self.cfg = application.config
        self.mod = self.getmodulefor(name)
        self.classname = cfg.getstring('%s.classname' % name, None)
        if self.classname is None:
            impl = self.mod
        else:
            try:
                impl = getattr(self.mod, self.classname)()
            except AttributeError:
                raise AttributeError(
                    "class %s does not exist on the specified module" % 
                    self.classname)
        self.impl = impl

    def loadpath(self):
        """ taken from mercurial.extensions """
        # generate a unique one to avoid clash
        name = "webscard.%s" % self.name
        name = name.replace('.','_')
        self.path = os.path.expanduser(os.path.expandvars(self.path))
        if os.path.isdir(self.path):
            # module/__init__.py style
            d, f = os.path.split(self.path.rstrip(os.path.sep))
            fd, fpath, desc = imp.find_module(f, [d])
            return imp.load_module(name, fd, fpath, desc)
        else:
            return imp.load_source(name, self.path)

    def getmodulefor(self):
        self.path = self.cfg.getstring('%s.path' % self.name, None)
        if self.path is not None:
            mod = self.loadpath()
        else:
            module = cfg.getstring('%s.module' % self.name, None)
            if module is None:
                if self.name == 'pyscard':
                    module = 'smartcard.scard'
                else:
                    raise ValueError(
                        '%s.module or %s.path config option missing' 
                        % self.name)
            mod = __import__(module)
            components = module.split('.')
            for comp in components[1:]:
                mod = getattr(mod, comp)
        print "mod is %s" % mod
        self.mod = mod

    def release(self, session):
        """ The sesion finished playing with his instance """
        pass

    def use(self, session):
        """ We are going to be used by this session """
        pass

    def isfree(self):
        """ If we can be used on one more session """
        return True

    def get(self, session):
        return impl

class Chooser(object):
    
    pool = []
    # map session to implementation
    map = {}
    def __init__(self):
        cfg = application.config
        impls = cfg.getstring('internal.implementations', 'pyscard')
        impls = impls.split()
        for implname in impls:
            self.pool.append(Implementation(implname))

    def acquire(self, session):
        free = []
        for impl in pool:
            if impl.isfree():
                free.append(impl)
        if len(free) != 0:
            impl = random.choice(free)
        impinst = impl.use(session)
        self.map[session.uid] = implinst
        return impl

    def get(self, session):
        return self.map[session.uid].get(session)

    def release(self, session):
        impl = self.map[session.uid]
        del self.map[session.uid]
        impl.release()

if __name__ == "__main__":
    import doctest
    doctest.testmod()
