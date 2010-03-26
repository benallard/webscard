from sqlalchemy import Table, Column, Integer, String, ForeignKey
from sqlalchemy.orm import mapper, relation
from webscard.utils import dbsession, metadata


handle_table = Table('handles', metadata,
    Column('uid', Integer, primary_key=True),
    Column('context_uid', Integer, ForeignKey('contexts.uid')),
    Column('value', Integer, nullable=False),
)

class Handle(object):
    """ It's here a SCARDHANDLE """
    query = dbsession.query_property()

    def __init__(self, value, context):
        self.value = value
        self.context_uid = context.uid
        context.handles.append(self)

    @property
    def implementation(self):
        return self.context.implementation

    @property
    def val(self):
        return long(self.value)

mapper(Handle, handle_table)

context_table = Table('contexts', metadata,
    Column('uid', Integer, primary_key=True),
    Column('value', Integer, nullable=False),
)

impls = {}

class Context(object):
    """ We are talking here about SCARDCONTEXT """
    query = dbsession.query_property()

    def __init__(self, value, implementation):
        self.value = value
        impls[value] = implementation
        dbsession.add(self)

    @property
    def implementation(self):
        try:
            return impls[self.value]
        except KeyError:
            return None

    @property
    def val(self):
        return long(self.value)

mapper(Context, context_table, properties={
    'handles': relation(Handle, backref='context')
})

