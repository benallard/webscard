from sqlalchemy import Table, Column, Integer, String
from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapper, relation

from webscard.utils import dbsession, metadata

from webscard.models.handle import Handle

transaction_table = Table('transactions', metadata,
    Column('uid', Integer, primary_key=True),
    Column('handle_uid', Integer, ForeignKey('handles.uid')),
    
)

class Transaction(object):
    query = dbsession.query_property()
    def __init__(self, hCard):
        self.hCard = hCard

mapper(Transaction, transaction_table,properties={
        'hCard': relation(Handle, backref='transactions'),
        }
)
