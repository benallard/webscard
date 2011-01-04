from sqlalchemy import Table, Column, Integer, Float, DateTime, String
from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapper, relation

from webscard.utils import dbsession, metadata

from webscard.models.handle import Context
from webscard.models.apdu import APDU

operation_table = Table('operations', metadata,
    Column('uid', Integer, primary_key=True),
    Column('context_uid', Integer, ForeignKey('contexts.uid')),
    Column('name', String),
    Column('duration', Float),
    Column('initiated', DateTime),
    Column('result', Integer),
    Column('type', String(20), nullable=False),
)

class Operation(object):
    query = dbsession.query_property()

    def __init__(self, name, context, **params):
        self.name = name
        self.context = context
        self.initiated = params.get('time')
        dbsession.add(self)
        dbsession.flush()

    def performed(self, hresult,  **params):
        self.result = hresult
        duration = params.get('time') - self.initiated
        self.duration = duration.days * 86400 + \
            duration.seconds + duration.microseconds * 1e-6

mapper(Operation, operation_table, 
    polymorphic_on=operation_table.c.type, polymorphic_identity='operation',
    properties = {'context': relation(Context, backref='operations')},
)

transmit_table = Table('transmits', metadata,
    Column('operation_uid', Integer, ForeignKey('operations.uid'), primary_key=True),
    Column('apdu_uid', Integer, ForeignKey('apdus.uid')),
    Column('protocol', Integer),
)

class Transmit(Operation):
    def __init__(self, name, context, **params):
        Operation.__init__(self, name, context, **params)
        self.apdu = APDU(self, params['apdu'])
        self.protocol = params['dwProtocol']

    def performed(self, hresult, **params):
        Operation.performed(self, hresult, **params)
        self.apdu.received(params['response'])
mapper(Transmit, transmit_table, inherits=Operation, polymorphic_identity='transmit',
    properties = {'apdu': relation(APDU)},
)

control_table = Table('controls', metadata,
    Column('operation_uid', Integer, ForeignKey('operations.uid'), primary_key=True),
    Column('controlcode', Integer),
    Column('inbuffer', String),
    Column('outbuffer', String),
)

class Control(Operation):
    def __init__(self, name, context, **params):
        Operation.__init__(self, name, context, **params)
        self.controlcode = params['dwControlCode']
        self.inbuffer = stringify(params['inbuffer'])

    def performed(self, hresult, **params):
        Operation.performed(self, hresult, **params)
        self.outbuffer = stringify(params['outbuffer'])
mapper(Control, control_table, inherits=Operation, polymorphic_identity='control')


class GetStatusChange(Operation):
    pass

class Status(Operation):
    pass

class ListReaders(Operation):
    pass

class Connect(Operation):
    pass

classdict = {
    'transmit': Transmit,
    'control': Control,
#    'getstatuschange': GetStatusChange,
#    'status': Status,
#    'listreaders': ListReaders,
}

def getclassfor(name):
    return classdict.get(name, Operation)
