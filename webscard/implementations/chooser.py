import imp, os, random, thread

import ConfigParser

from datetime import timedelta

from webscard.utils import application
from webscard.models.session import Session

TIMEOUT = timedelta(minutes = 5)

THRESHOLD = 20

def createimpl(name):
    cfg = application.config
    if not cfg.has_section(name):
        raise ValueError("section [%s] in the config file is missing" % name)
    mod = getmodulefor(name)
    classname = cfg.getstring('%s.classname' % name, None)
    hard = cfg.getbool('%s.hard' % name, False)
    if classname is None:
        impl = mod
    else:
        try:
            impl = getattr(mod, classname)
        except AttributeError:
            raise AttributeError(
                "class %s does not exist on the specified module" %
                classname)
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
        except ConfigParser.NoOptionError:
            free = True
        if isinstance(free, bool):
            free = lambda: free
        elif isinstance(free, str):
            free = getattr(impl, free)
        else:
            raise ValueError(free)
        res['free'] = free

        acquirename = cfg.getstring('%s.acquire' % name, None)
        if acquirename is not None:
            acquirefunc = getattr(impl, acquirename)
        else:
            acquirefunc = lambda s: impl
        res['acquire'] = acquirefunc

        def generatefunction(impl):
            releasecontext = impl.SCardReleaseContext
            def releaseremainingcontexts(session):
                for c in session.contexts:
                    if not c.isreleased():
                        releasecontext(c.val)
            return releaseremainingcontexts

        releasename = cfg.getstring('%s.release' % name, None)
        if releasename is not None:
            releasefunc = getattr(impl, releasename)
        else:
            releasefunc = generatefunction(impl)
        res['release'] = releasefunc

    return res

def loadpath(path, name):
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
                % (name, name))
        mod = __import__(module)
        components = module.split('.')
        for comp in components[1:]:
            mod = getattr(mod, comp)
    print "mod is %s" % mod
    return mod

POOL = []
# map session to implementation and name
MAP = {}
MAPMUTEX = thread.allocate_lock()
def initialize():
    impls =  application.config.getimplementations()
    for implname in impls:
        POOL.append(createimpl(implname))


def releaseoldestexpiredsession(name, current):
    bad = None
    badinactivity = TIMEOUT
    MAPMUTEX.acquire()
    for session_uid in MAP:
        if MAP[session_uid]['name'] == name:
            session = Session.query.get(session_uid)
            inactivity = session.inactivity()
            if inactivity > badinactivity:
                bad = session_uid
                badinactivity = inactivity
    MAPMUTEX.release()
    if bad is not None:
        release(bad, current)
        return True
    return False

def cleanexpiredsoftsessions(current):
    expired = []
    MAPMUTEX.acquire()
    for session_uid in MAP:
        if not MAP[session_uid]['hard']:
            session = Session.query.get(session_uid)
            if session.inactivity() > TIMEOUT:
                expired.append(session)
            else:
                print "leaving session with inactivity below timeout: %s" \
                    % session.inactivity()
    MAPMUTEX.release()
    print "cleaning %d sessions" % len(expired)
    for session in expired:
        release(session, current)
    print "%d active sessions remaining" % len(MAP)

def release(session, current):
    impl = MAP[session.uid]
    del MAP[session.uid]
    session.closedby = current
    # call the release function from the pool
    for i in POOL:
        if i['name'] == impl['name']:
            i['release'](session)

def instanciateimpl(impl, session):
    if impl['hard']:
        implinst = impl['acquire'](session)
    else:
        if impl['class']:
            implinst = imp['impl'](impl['name'], application.config)
        else:
            implinst = impl['impl']
    return implinst

def acquire(session):
    print "acquire (%d)" % session.uid
    free = []
    for impl in POOL:
        if impl['hard']:
            if (releaseoldestexpiredsession(impl['name'], session) or
                impl['free']()):
                free.append(impl)
        else:
            free.append(impl)

    
    if len(MAP) > THRESHOLD:
        cleanexpiredsoftsessions(session)
    
    if len(free) != 0:
        impl = random.choice(free)

    implinst = instanciateimpl(impl, session)
    MAPMUTEX.acquire()
    MAP[session.uid]  = {}
    MAP[session.uid]['inst'] = implinst
    MAP[session.uid]['name'] = impl['name']
    MAP[session.uid]['hard'] = impl['hard']
    MAPMUTEX.release()
    return implinst

def get(session):
    return map[session.uid]['inst']
