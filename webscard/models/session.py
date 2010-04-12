from datetime import datetime

from sqlalchemy import Table, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import mapper, relation, relationship, backref

from werkzeug import cached_property

from webscard.utils import dbsession, metadata, application
from webscard.models.handle import Context, Handle
from webscard.implementations import chooser

from smartcard.scard import SCARD_E_INVALID_HANDLE, SCARD_E_INVALID_PARAMETER

session_table = Table('sessions', metadata,
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
    impl = None

    def __init__(self, request):
        self.user_agent = request.headers.get('User-Agent')
        self.remote_addr = request.remote_addr
        self.firstactivity = datetime.now()
        self.update()
        dbsession.add(self)
        dbsession.flush() # that will assign us a uid
        self.impl = chooser.acquire(self)

    def validatecontext(self, context):
        hContext = Context.query.get(context)
        if hContext is None:
            return {'message': "Context %d does not exists" % context,
                    'hresult': SCARD_E_INVALID_PARAMETER}
        if hContext not in self.contexts:
            return {'message': "Current session #%d is not #%d where the" \
                        " context has been aquired" % (self.uid,
                                                       hContext.session.uid),
                    'hresult': SCARD_E_INVALID_PARAMETER}
        return None

    def validatehandle(self, handle):
        hHandle = Handle.query.get(handle)
        if hHandle is None:
            return {'message': "Handle %d never seen" % handle,
                    'hresult': SCARD_E_INVALID_HANDLE}
        res = False
        for hContext in self.contexts:
            if hHandle in hContext.handles:
                res = True
        if not res:
            return {'message': "Current handle #%d does not belong to any " \
                        "context opened in this session #%d" % (hHandle.uid,
                                                                self.uid),
                    'hresult': SCARD_E_INVALID_HANDLE}
        return None

    @cached_property
    def implementation(self):
        return chooser.get(self)

    def __repr__(self):
        return "<session #%d, %d contexts, inactive for %s>" % (
            self.uid, len(self.contexts), self.inactivity())

    def update(self):
        self.lastactivity = datetime.now()

    def inactivity(self):
        return datetime.now() - self.lastactivity

    def asdict(self):
        res = {}
        res['uid'] = self.uid
        res['user_agent'] = self.user_agent
        res['remote_addr'] = self.remote_addr
        res['firstactivity'] = str(self.firstactivity)
        res['inactivity'] = str(self.inactivity())
        res['contexts'] = []
        for c in self.contexts:
            res['contexts'].append(c.uid)
        if self.closedby_uid is not None:
            res['closed_by'] = self.closedby_uid
        return res

mapper(Session, session_table, properties={
    'contexts': relation(Context, backref='session'),
    # adjency list pattern
    'hasclosed': relation(Session, backref=backref('closedby', remote_side=[session_table.c.uid])),
})
