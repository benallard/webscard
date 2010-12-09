"""
Our own garbage collector that tries to cleanup the old sessions
"""
from datetime import timedelta

from webscard.implementations import MAP, MAPMUTEX, POOL
from webscard.models.session import Session

TIMEOUT = timedelta(minutes = 5)
THRESHOLD = 20

def run(current):
    for impl in POOL:
        if impl['hard']:
            releaseoldestexpiredsession(impl['name'], current)

    if len(MAP) > THRESHOLD:
        cleanexpiredsoftsessions(current)

def release(session, current):
    impl = MAP[session.uid]
    del MAP[session.uid]
    session.closedby = current
    # call the release function from the pool
    for i in POOL:
        if i['name'] == impl['name']:
            i['release'](session)

def releaseoldestexpiredsession(name, current):
    """
    This cleanup the oldest expired session, 
    basically to make space in the MAP
    """
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
    """
    All the expired soft sessions are cleanup up, this happen upon threshold
    """
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
