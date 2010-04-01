from datetime import datetime

from sqlalchemy import Table, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import mapper, relation

from werkzeug.exceptions import Unauthorized, NotFound

from webscard.utils import dbsession, metadata, application
from webscard.models.handle import Context


session_table = Table('sessions', metadata,
    Column('uid', Integer, primary_key=True),
    Column('user_agent', Text),
    Column('remote_addr', String(15)),
    Column('firstactivity', DateTime),
    Column('lastactivity', DateTime),
)

impls = {}

class Session(object):
    """ We store here HTTP session """
    query = dbsession.query_property()
    shouldsave = False
    impl = None

    def __init__(self, request, implementation):
        self.impl = implementation
        self.user_agent = request.headers['User-Agent']
        self.remote_addr = request.remote_addr
        self.firstactivity = datetime.now()
        dbsession.add(self)

    def store(self):
        if self.uid is None:
            raise ValueError(self.uid)
        impls[self.uid] = self.impl

    def validatecontext(self, context):
        if context is None:
            raise NotFound("Requested context does not exists")
        if not application.config.getbool('internal.sessioncheck', True):
            return
        if context not in self.contexts:
            raise Unauthorized("Current session #%d is not #%d where the"
                               " context has been aquired" % (self.uid,
                               context.session.uid))

    def validatehandle(self, handle):
        if handle is None:
            return NotFound("Requested handle does not exists")
        if not application.config.getbool('internal.sessioncheck', True):
            return
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

    def update(self):
        self.lastactivity = datetime.now()

mapper(Session, session_table, properties={
    'contexts': relation(Context, backref='session')
})
