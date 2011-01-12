"""
This is for HTTP session storage in database
"""

from datetime import datetime

from sqlalchemy import Table, Column, Integer, String, Text, DateTime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapper, relation, backref

from werkzeug import cached_property

from webscard.utils import dbsession, metadata
from webscard.models.handle import Context, Handle

from smartcard.scard import SCARD_E_INVALID_HANDLE, SCARD_E_INVALID_PARAMETER

SESSION_TABLE = Table('sessions', metadata,
    Column('uid', Integer, primary_key=True),
    Column('user_agent', Text),
    Column('remote_addr', String(15)),
    Column('firstactivity', DateTime),
    Column('lastactivity', DateTime),
    Column('closedby_uid', Integer, ForeignKey('sessions.uid')),
)

class Session(object):
    """ We store here HTTP session """
    query = dbsession.query_property()

    def __init__(self, request):
        self.user_agent = request.headers.get('User-Agent')
        self.remote_addr = request.remote_addr
        self.firstactivity = datetime.now()
        self.lastactivity = None
        self.update()
        dbsession.add(self)
        dbsession.flush()

    def validatecontext(self, context_uid):
        """ Does the context belong to this session """
        context = Context.query.get(context_uid)
        if context is None:
            return {'message': "Context %d does not exists" % context_uid,
                    'hresult': SCARD_E_INVALID_PARAMETER}
        if context not in self.contexts:
            return {'message': "Current session #%d is not #%d where the" \
                        " context has been aquired" % (self.uid,
                                                       context.session.uid),
                    'hresult': SCARD_E_INVALID_PARAMETER}
        return None

    def validatehandle(self, handle_uid):
        """ Does the SCARDHANDLE belong to that session """
        handle = Handle.query.get(handle_uid)
        if handle is None:
            return {'message': "Handle %d never seen" % handle_uid,
                    'hresult': SCARD_E_INVALID_HANDLE}
        res = False
        for context in self.contexts:
            if handle in context.handles:
                res = True
        if not res:
            return {'message': "Current handle #%d does not belong to any " \
                        "context opened in this session #%d" % (handle.uid,
                                                                self.uid),
                    'hresult': SCARD_E_INVALID_HANDLE}
        return None

    def __repr__(self):
        return "<session #%d, %d contexts, inactive for %s>" % (
            self.uid, len(self.contexts), self.inactivity())

    def update(self):
        self.lastactivity = datetime.now()

    def inactivity(self):
        """ How long did the session has been inactive """
        return datetime.now() - self.lastactivity

mapper(Session, SESSION_TABLE, properties={
    'contexts': relation(Context, backref='session'),
    # adjency list pattern
    'hasclosed': relation(Session, backref=backref(
                'closedby', remote_side=[SESSION_TABLE.c.uid])),
})
