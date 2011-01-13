from sqlalchemy import Table, Column, Integer, Float, DateTime, String
from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapper, relation, backref

from webscard.utils import dbsession, metadata, stringify

from webscard.models.handle import Context, Handle
from webscard.models.apdu import APDU
from webscard.models.reader import Reader

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
        self.apdu = APDU(params['apdu'])
        self.protocol = params['dwProtocol']

    def performed(self, hresult, **params):
        Operation.performed(self, hresult, **params)
        self.apdu.received(params['response'])
mapper(Transmit, transmit_table, inherits=Operation, polymorphic_identity='transmit',
    properties = {'apdu': relation(APDU, backref="operation")},
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

connect_table = Table('connects', metadata,
    Column('operation_uid', Integer, ForeignKey('operations.uid'), primary_key=True),
    Column('reader_uid', Integer, ForeignKey('readers.uid')),
    Column('sharedmode', Integer),
    Column('preferredprotocols', Integer),
    Column('handle_uid', Integer, ForeignKey('handles.uid')),
    Column('activeprotocol', Integer),
)
class Connect(Operation):
    def __init__(self, name, context, **params):
        Operation.__init__(self, name, context, **params)
        self.reader = Reader.get(params['szReader'])
        self.sharedmode = params['dwSharedMode']
        self.preferredprotocols = params['dwPreferredProtocols']

    def performed(self, hresult, **params):
        Operation.performed(self, hresult, **params)
        self.hCard = params['hCard']
        self.hCard.reader = self.reader
        self.activeprotocol = params['dwActiveProtocol']
mapper(Connect, connect_table, inherits=Operation, polymorphic_identity='connect',
       properties={'reader':relation(Reader),
                   'hCard':relation(Handle, backref=backref('opened_by', uselist=False))}
)

disconnect_table = Table('disconnects', metadata,
    Column('operation_uid', Integer, ForeignKey('operations.uid'), primary_key=True),
    Column('handle_uid', Integer, ForeignKey('handles.uid')),
    Column('disposition', Integer),
)
class Disconnect(Operation):
    def __init__(self, name, context, **params):
        Operation.__init__(self, name, context, **params)
        self.hCard = params['hCard']
        self.disposition = params['dwDisposition']
mapper(Disconnect, disconnect_table, inherits=Operation, polymorphic_identity='disconnect',
       properties={'hCard':relation(Handle, backref='closed_by')}
)

establishcontext_table = Table('establishcontexts', metadata,
    Column('operation_uid', Integer, ForeignKey('operations.uid'), primary_key=True),
    Column('scope', Integer),
)
class EstablishContext(Operation):
    def __init__(self, name, context, **params):
        Operation.__init__(self, name, context, **params)
        self.scope = params['dwScope']
        self.context.opened_by = self
mapper(EstablishContext, establishcontext_table, inherits=Operation, polymorphic_identity='establishcontext',
       properties={'context':relation(Context, backref=backref('opened_by', uselist=False))}
)

releasecontext_table = Table('releasecontext', metadata,
    Column('operation_uid', Integer, ForeignKey('operations.uid'), primary_key=True),
)
class ReleaseContext(Operation):
    def __init__(self, name, context, **params):
        Operation.__init__(self, name, context, **params)
        self.context.closed_by.append(self)
mapper(ReleaseContext, releasecontext_table, inherits=Operation, polymorphic_identity='releasecontext',
       properties={'context':relation(Context, backref='closed_by')}
)

class GetStatusChange(Operation):
    pass

class Status(Operation):
    pass

class ListReaders(Operation):
    pass

classdict = {
    'transmit': Transmit,
    'control': Control,
    'connect': Connect,
    'disconnect': Disconnect,
    'establishcontext': EstablishContext,
    'releasecontext': ReleaseContext,
}

def getclassfor(name):
    return classdict.get(name, Operation)
