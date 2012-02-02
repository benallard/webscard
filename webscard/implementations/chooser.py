import imp, os, random

import ConfigParser

from webscard.utils import application, loadpath

from webscard.implementations import MAP, MAPMUTEX, POOL
from webscard.implementations import gc

def createimpl(name):
    cfg = application.config
    if not name in cfg:
        raise ValueError("section [%s] in the config file is missing" % name)
    cfg = cfg[name]
    mod = getmodulefor(name)
    classname = cfg.get('classname')
    hard = cfg.get('hard', False)
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
            free = cfg['free']
        except KeyError:
            free = True
        if isinstance(free, bool):
            free = lambda: free
        elif isinstance(free, str):
            free = getattr(impl, free)
        else:
            raise ValueError(free)
        res['free'] = free

        acquirename = cfg.get('acquire')
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

        releasename = cfg.get('release')
        if releasename is not None:
            releasefunc = getattr(impl, releasename)
        else:
            releasefunc = generatefunction(impl)
        res['release'] = releasefunc

    return res

def getmodulefor(name):
    cfg = application.config[name]
    path = cfg.get('path')
    if path is not None:
        # generate a unique one to avoid clash
        mod = loadpath(path, "webscard.%s" % name)
    else:
        module = cfg.get('module')
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

def initialize():
    impls =  application.config.getimplementations()
    for implname in impls:
        POOL.append(createimpl(implname))

def instanciateimpl(impl, session):
    if impl['hard']:
        implinst = impl['acquire'](session)
    else:
        if impl['class']:
            implinst = impl['impl'](impl['name'], application.config)
        else:
            implinst = impl['impl']
    return implinst

def getcandidates():
    free = []
    for candidate in POOL:
        if candidate['hard']:
            if candidate['free']():
                free.append(candidate)
        else:
            free.append(candidate)
    return free

def acquire(session):
    print "acquire (%d)" % session.uid
    free = getcandidates()

    if len(free) == 0:
        gc.run(session)
    
    free = getcandidates()

    if len(free) == 0:
        impl = createimpl('empty')
    else:
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
    return MAP[session.uid]['inst']
