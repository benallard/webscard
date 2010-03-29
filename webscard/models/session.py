from sqlalchemy import Table, Column, Integer
from sqlalchemy.orm import mapper, relation

from werkzeug.exceptions import Unauthorized

from webscard.utils import dbsession, metadata
from webscard.models.handle import Context


session_table = Table('sessions', metadata,
    Column('uid', Integer, primary_key=True)
)

impls = {}

class Session(object):
    """ We store here HTTP session """
    query = dbsession.query_property()
    shouldsave = False
    impl = None

    def __init__(self, implementation):
        self.impl = implementation
	self.shouldsave = True
        dbsession.add(self)

    def store(self):
        if self.uid is None:
            raise ValueError(self.uid)
        impls[self.uid] = self.impl

    def validatecontext(self, context):
        if context not in self.contexts:
            raise Unauthorized("Current session #%d is not #%d where the"
                               " context has been aquired" % (self.uid,
                               context.session.uid))

    def validatehandle(self, handle):
        res = False
        for context in self.contexts:
            if handle in context.handles:
                res = True
        if not res:
            raise Unauthorized("Current handle #%d does not belong to any "
                               "context opened in this session #%d" %(handle.uid,
                               self.uid))

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
