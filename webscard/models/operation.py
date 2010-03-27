from sqlalchemy import Table, Column, Integer, Float, DateTime, String
from sqlalchemy.orm import mapper

from webscard.utils import dbsession, metadata

operation_table = Table('operations', metadata,
    Column('uid', Integer, primary_key=True),
    Column('duration', Float),
    Column('initiated', DateTime),
    Column('result', Integer),
    Column('type', String, nullable=False),
)

class Operation(object):
    pass
mapper(Operation, operation_table, polymorphic_on=operation_table.c.type, polymorphic_identity='operation')

class EstablishContext(Operation):
    pass

class ReleaseContext(Operation):
    pass
