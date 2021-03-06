from sqlalchemy import Table, Column, Integer, Float, DateTime, String, Text
from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapper, relation, backref

from webscard.utils import dbsession, metadata, stringify

from webscard.models.handle import Context, Handle
from webscard.models.apdu import APDU
from webscard.models.reader import Reader
from webscard.models.atr import ATR
from webscard.models.transaction import Transaction

operation_table = Table('operations', metadata,
    Column('uid', Integer, primary_key=True),
    Column('context_uid', Integer, ForeignKey('contexts.uid')),
    Column('name', String(20)),
    Column('duration', Float),
    Column('initiated', DateTime),
    Column('result', Integer),
    Column('type', String(20), nullable=False),
)

class Operation(object):
    query = dbsession.query_property()

    def __init__(self, name, context, **params):
        self.name = name
        self.context = Context.query.get(context)
        self.initiated = params.get('time')

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
    Column('inbuffer', Text),
    Column('outbuffer', Text),
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
        self.hCard = Handle.query.get(params['hCard'])
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
        self.hCard = Handle.query.get(params['hCard'])
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

status_table = Table('statuses', metadata,
    Column('operation_uid', Integer, ForeignKey('operations.uid'), primary_key=True),
    Column('handle_uid', Integer, ForeignKey('handles.uid')),
    Column('reader_uid', Integer, ForeignKey('readers.uid')),
    Column('state', Integer),
    Column('protocol', Integer),
    Column('atr_uid', Integer, ForeignKey('atrs.uid')),
)
class Status(Operation):
    def __init__(self, name, context, **params):
        Operation.__init__(self, name, context, **params)
        self.hCard = Handle.query.get(params['hCard'])
    def performed(self, hresult, **params):
        Operation.performed(self, hresult, **params)
        if hresult == 0:
            self.reader = Reader.get(params['szReaderName'])
            self.ATR = ATR.get(params['ATR'])
        self.state = params['dwState']
        self.protocol = params['dwProtocol']
mapper(Status, status_table, inherits=Operation, polymorphic_identity='status',
       properties={'hCard':relation(Handle),
                   'reader': relation(Reader),
                   'ATR':relation(ATR),},
)

begintransaction_table = Table('begintransactions', metadata,
    Column('operation_uid', Integer, ForeignKey('operations.uid'), primary_key=True),
    Column('handle_uid', Integer, ForeignKey('handles.uid')),
    Column('transaction_uid', Integer, ForeignKey('transactions.uid')),
)
class BeginTransaction(Operation):
    def __init__(self, name, context, **params):
        Operation.__init__(self, name, context, **params)
        self.hCard = Handle.query.get(params['hCard'])
    def performed(self, hresult, **params):
        Operation.performed(self, hresult, **params)
        if (hresult == 0):
            self.transaction = Transaction(self.hCard)
mapper(BeginTransaction, begintransaction_table, inherits=Operation, polymorphic_identity='begintransaction',
       properties={'hCard':relation(Handle),
                   'transaction':relation(Transaction, backref=backref('opened_by', uselist=False))},
)

endtransaction_table = Table('endtransactions', metadata,
    Column('operation_uid', Integer, ForeignKey('operations.uid'), primary_key=True),
    Column('handle_uid', Integer, ForeignKey('handles.uid')),
    Column('disposition', Integer),
    Column('transaction_uid', Integer, ForeignKey('transactions.uid')),
)
class EndTransaction(Operation):
    def __init__(self, name, context, **params):
        Operation.__init__(self, name, context, **params)
        self.hCard = Handle.query.get(params['hCard'])
        self.disposition = params['dwDisposition']
    def performed(self, hresult, **params):
        Operation.performed(self, hresult, **params)
        if (hresult == 0):
            for transaction in reversed(self.hCard.transactions):
                if not transaction.closed_by:
                    self.transaction = transaction
                    break
mapper(EndTransaction, endtransaction_table, inherits=Operation, polymorphic_identity='endtransaction',
       properties={'hCard':relation(Handle),
                   'transaction':relation(Transaction, backref=backref('closed_by', uselist=False))},
)

classdict = {
    'transmit': Transmit,
    'control': Control,
    'connect': Connect,
    'disconnect': Disconnect,
    'establishcontext': EstablishContext,
    'releasecontext': ReleaseContext,
    'status': Status,
    'begintransaction': BeginTransaction,
    'endtransaction': EndTransaction,
}

def getclassfor(name):
    return classdict.get(name, Operation)
