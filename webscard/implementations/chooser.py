import imp, os, random

from datetime import timedelta

from webscard.utils import application

TIMEOUT = timedelta(0, 5* 60)

THRESHOLD = 20

def createimpl(name):
    cfg = application.config
    mod = getmodulefor(name)
    classname = cfg.getstring('%s.classname' % name, None)
    hard = cfg.getbool('%s.hardware' % name, False)
    if classname is None:
        impl = mod
    else:
        try:
            impl = getattr(mod, classname)
        except AttributeError:
            raise AttributeError(
                "class %s does not exist on the specified module" %
                self.classname)
        if hard:
            # There is one class to manage everything
            impl = impl()

    res =  { 'name':name,
             'impl':impl,
             'hard': hard,
             'class': bool(classname),
             }

    if hard:
        try:
            free = cfg.get(name, 'free')
        except NoOptionError:
            free = True
        if isinstance(free, bool):
            free = lambda: free
        elif isinstance(free, str):
            free = getattr(impl, free)
        else:
            raise ValueError(free)
        res['free'] = free

        acquire = cfg.getstring('%s.acquire' % name, None)
        if acquire is not None:
            acquire = getattr(impl, acquire)
        else:
            acquire = lambda s: impl
        res['acquire'] = acquire

        release = cfg.get('%s.release' % name, None)
        if release is not None:
            release = getattr(impl, release)
        else:
            release = lambda s: s
        res['release'] = release

    return res

def loadpath(path, name):
    """ taken from mercurial.extensions """
    cfg = application.config
    name = name.replace('.','_')
    path = os.path.expanduser(os.path.expandvars(path))
    if os.path.isdir(path):
        # module/__init__.py style
        d, f = os.path.split(path.rstrip(os.path.sep))
        fd, fpath, desc = imp.find_module(f, [d])
        return imp.load_module(name, fd, fpath, desc)
    else:
        return imp.load_source(name, path)

def getmodulefor(name):
    cfg = application.config
    path = cfg.getstring('%s.path' % name, None)
    if path is not None:
        # generate a unique one to avoid clash
        mod = loadpath(path, "webscard.%s" % name)
    else:
        module = cfg.getstring('%s.module' % name, None)
        if module is None:
            raise ValueError(
                '%s.module or %s.path config option missing'
                % name)
        mod = __import__(module)
        components = module.split('.')
        for comp in components[1:]:
            mod = getattr(mod, comp)
    print "mod is %s" % mod
    return mod

pool = []
# map session to implementation and name
map = {}
def initialize():
    cfg = application.config
    impls = cfg.getstring('internal.implementations', 'pyscard')
    impls = impls.split()
    for implname in impls:
        pool.append(createimpl(implname))


def releaseoldestexpiredsession(name):
    bad = None
    badinactvity = TIMEOUT
    for session_uid in map:
        if map[session_uid]['name'] == name:
            session = Session.query.get(session_uid)
            inactivity = session.inactivity()
            if inactivity > badinactivity:
                bad = session_uid
                badinactivity = inactivity
    if bad is not None:
        release(bad)
        return True
    return False

def cleanexpiredsoftsessions():
    expired = []
    for session_uid in map:
        if not map[session_uid]['hard']:
            session = Session.query.get(session_uid)
            if session.inactivity() > TIMEOUT:
                expired.append(session)
    for session in expired:
        release(session.uid)

def acquire(session):
    free = []
    for impl in pool:
        if impl['hard']:
            if impl['free']():
                free.append(impl)
            else:
                if releaseoldestexpiredsession(impl['name']):
                    free.append(impl)
        else:
            free.append(impl)

    
    if len(map) > THRESHOLD:
        cleanexpiredsoftsessions()
    
    if len(free) != 0:
        impl = random.choice(free)

    if impl['hard']:
        implinst = impl['acquire'](session)
    else:
        if impl['class']:
            implinst = imp['impl']()
        else:
            implinst = impl['impl']
    map[session.uid]  = {}
    map[session.uid]['inst'] = implinst
    map[session.uid]['name'] = impl['name']
    return implinst

def get(session):
    return map[session.uid]['inst']

def release(session):
    impl = map[session.uid]
    del map[session.uid]
    for i in pool:
        if i['name'] == impl['name']:
            i['release'](session)
