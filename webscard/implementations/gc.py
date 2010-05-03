"""
Our own garbage collector that tries to cleanup the old sessions
"""

from webscard.implementations import MAP, MAPMUTEX
from webscard.models.session import Session

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
