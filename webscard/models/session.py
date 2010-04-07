from sqlalchemy import Table, Column, Integer
from sqlalchemy.orm import mapper, relation

from werkzeug.exceptions import Unauthorized

from webscard.utils import dbsession, metadata, application
from webscard.models.handle import Context, Handle

from smartcard.scard import SCARD_E_INVALID_HANDLE, SCARD_E_INVALID_PARAMETER

from webscard import implementations

session_table = Table('sessions', metadata,
    Column('uid', Integer, primary_key=True)
)

impls = {}

class Session(object):
    """ We store here HTTP session """
    query = dbsession.query_property()
    shouldsave = False
    impl = None

    def __init__(self):
        self.impl = implementations.getone()
	self.shouldsave = True
        dbsession.add(self)

    def store(self):
        if self.uid is None:
            raise ValueError(self.uid)
        impls[self.uid] = self.impl

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

    @property
    def implementation(self):
	if self.impl is None:
            self.impl = impls[self.uid]
        return self.impl

    def __repr__(self):
        return "<session %d>" % self.uid

mapper(Session, session_table, properties={
    'contexts': relation(Context, backref='session')
})
