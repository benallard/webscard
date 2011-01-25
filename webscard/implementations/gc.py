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
            candidate = getoldestexpiredsession(impl['name'])
            while ((candidate is not None) and
                   not (release(candidate, current))):
                candidate = getoldestexpiredsession(impl['name'])

    if len(MAP) > THRESHOLD:
        cleanexpiredsoftsessions(current)

def release(session, current):
    impl = MAP[session.uid]
    del MAP[session.uid]
    session.closedby = current
    # call the release function from the pool
    for i in POOL:
        if i['name'] == impl['name']:
            return i['release'](session)

def getoldestexpiredsession(name):
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
                bad = session
                badinactivity = inactivity
            else:
                print "inactivity too short: %s" % inactivity
    MAPMUTEX.release()
    return bad

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
