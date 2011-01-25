from sqlalchemy import Table, Column, Integer, Text
from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapper, relation

from webscard.utils import dbsession, metadata

from webscard.models.handle import Handle

reader_table = Table('readers', metadata,
    Column('uid', Integer, primary_key=True),
    Column('name', Text, nullable=False),
)

class Reader(object):
    query = dbsession.query_property()

    def __init__(self, name):
        self.name = name

    @classmethod
    def get(cls, szReader):
        potential = cls.query.filter_by(name=szReader).first()
        return potential or cls(szReader)
            

mapper(Reader, reader_table,properties={
    'handles': relation(Handle, backref='reader')
})
