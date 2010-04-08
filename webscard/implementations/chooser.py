import imp, os

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

    def loadpath(self, path, name):
        """ taken from mercurial.extensions """
        name = name.replace('.','_')
        path = os.path.expanduser(os.path.expandvars(path))
        if os.path.isdir(path):
            # module/__init__.py style
            d, f = os.path.split(path.rstrip(os.path.sep))
            fd, fpath, desc = imp.find_module(f, [d])
            return imp.load_module(name, fd, fpath, desc)
        else:
            return imp.load_source(name, path)

    def getmodulefor(self, name):
        cfg = application.config
        path = cfg.getstring('%s.path' % name, None)
        if path is not None:
            # Generate a unique name to avoid clash
            mod = self.loadpath(path, 'webscard.%s' % name)
        else:
            module = cfg.getstring('%s.module' % name, None)
            if module is None:
                if name == 'pyscard':
                    module = 'smartcard.scard'
                else:
                    raise ValueError(
                        '%s.module or %s.path config option missing' % name)
            mod = __import__(module)
            components = module.split('.')
            for comp in components[1:]:
                mod = getattr(mod, comp)
        print "mod is %s" % mod
        return mod

    def create(self, name):
        cfg = application.config
        mod = self.getmodulefor(name)
        classname = cfg.getstring('%s.classname' % name, None)
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

