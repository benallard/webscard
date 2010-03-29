from sqlalchemy import Table, Column, Integer
from sqlalchemy.orm import mapper, relation

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

    @property
    def implementation(self):
	if self.impl is None:
            self.impl = impls[self.uid]
        return self.impl
mapper(Session, session_table, properties={
    'contexts': relation(Context, backref='session')
})
