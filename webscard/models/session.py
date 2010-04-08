from datetime import datetime

from sqlalchemy import Table, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import mapper, relation

from werkzeug import cached_property

from webscard.utils import dbsession, metadata, application
from webscard.models.handle import Context, Handle

from smartcard.scard import SCARD_E_INVALID_HANDLE, SCARD_E_INVALID_PARAMETER

session_table = Table('sessions', metadata,
    Column('uid', Integer, primary_key=True),
    Column('user_agent', Text),
    Column('remote_addr', String(15)),
    Column('firstactivity', DateTime),
    Column('lastactivity', DateTime),
)

class Session(object):
    """ We store here HTTP session """
    query = dbsession.query_property()
    impl = None

    def __init__(self, request):
        self.impl = application.implchooser.acquire(self)
        self.user_agent = request.headers.get('User-Agent')
        self.remote_addr = request.remote_addr
        self.firstactivity = datetime.now()
        dbsession.add(self)
        dbsession.flush() # that will assign us a uid
        self.store()

    def store(self):
        assert self.uid, "No uid on the session, no one flushed !"
        application.implchooser.setimpl(self, self.impl)

    def validatecontext(self, context):
        hContext = Context.query.get(context)
        if hContext not in self.contexts:
            return {'message': "Current session #%d is not #%d where the" \
                        " context has been aquired" % (self.uid,
                                                       hContext.session.uid),
                    'hresult': SCARD_E_INVALID_PARAMETER}
        return None

    def validatehandle(self, handle):
        handle = Handle.query.get(handle)
        res = False
        for hContext in self.contexts:
            if handle in hContext.handles:
                res = True
        if not res:
            return {'message': "Current handle #%d does not belong to any " \
                        "context opened in this session #%d" % (handle.uid,
                                                                self.uid),
                    'hresult': SCARD_E_INVALID_HANDLE}
        return None

    @cached_property
    def implementation(self):
        return application.implchooser.getimpl(self)

    def __repr__(self):
        return "<session %d>" % self.uid

    def update(self):
        self.lastactivity = datetime.now()

mapper(Session, session_table, properties={
    'contexts': relation(Context, backref='session')
})
