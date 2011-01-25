from sqlalchemy import Table, Column, Integer, String
from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapper, relation

from webscard.utils import dbsession, metadata, stringify

atr_table = Table('atrs', metadata,
    Column('uid', Integer, primary_key=True),
    Column('canonical', String),
)

class ATR(object):
    query = dbsession.query_property()

    def __init__(self, atr):
        self.bytes = atr
        self.canonical = stringify(atr)

    @classmethod
    def get(cls, bytes):
        potential = cls.query.filter_by(canonical=stringify(bytes)).first()
        return potential or cls(bytes)
            

mapper(ATR, atr_table)
