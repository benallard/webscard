from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import mapper, relation
from webscard.utils import dbsession, metadata


handle_table = Table('handles', metadata,
    Column('uid', Integer, primary_key=True),
    Column('context_uid', Integer, ForeignKey('contexts.uid')),
    Column('value', Integer, nullable=False),
    Column('reader_uid', Integer, ForeignKey('readers.uid'))
)

class Handle(object):
    """ It's here a SCARDHANDLE """
    query = dbsession.query_property()

    def __init__(self, value, context):
        self.value = value
        self.context_uid = context.uid
        context.handles.append(self)
        dbsession.add(self)
        dbsession.flush()

    @property
    def val(self):
        return long(self.value)

mapper(Handle, handle_table)

context_table = Table('contexts', metadata,
    Column('uid', Integer, primary_key=True),
    Column('value', Integer, nullable=False),
    Column('session_uid', Integer, ForeignKey('sessions.uid')),
)

class Context(object):
    """ We are talking here about SCARDCONTEXT """
    query = dbsession.query_property()

    def __init__(self, session, value, implementation):
        self.session_uid = session.uid
        self.value = value
        dbsession.add(self)
        dbsession.flush()

    @property
    def val(self):
        return long(self.value)

mapper(Context, context_table, properties={
    'handles': relation(Handle, backref='context')
})

