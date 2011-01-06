from sqlalchemy import Table, Column, Integer, String
from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapper, relation

from webscard.utils import dbsession, metadata

from webscard.models.handle import Context, Handle

reader_table = Table('readers', metadata,
    Column('uid', Integer, primary_key=True),
    Column('name', String, nullable=False),
)

class Reader(object):
    query = dbsession.query_property()

    def __init__(self, name):
        self.name = name
        dbsession.add(self)
        dbsssion.flush()

mapper(Reader, reader_table,properties={
    'handles': relation(Handle, backref='reader')
})
