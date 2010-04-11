from sqlalchemy import Table, Column, Integer, Float, DateTime, String
from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapper, relation, backref

from webscard.utils import dbsession, metadata

from webscard.models.handle import Context

operation_table = Table('operations', metadata,
    Column('uid', Integer, primary_key=True),
    Column('context_uid', Integer, ForeignKey('contexts.uid')),
    Column('duration', Float),
    Column('initiated', DateTime),
    Column('result', Integer),
    Column('type', String(20), nullable=False),
)

class Operation(object):
    query = dbsession.query_property()

    def __init__(self, **params):
        self.initiated = params.get('time')
        self.context = params['context']
        dbsession.add(self)

mapper(Operation, operation_table, 
    polymorphic_on=operation_table.c.type, polymorphic_identity='operation',
    properties = {'context': relation(Context, backref='operations')},
)

class EstablishContext(Operation):
    pass

class ReleaseContext(Operation):
    pass
