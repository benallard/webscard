from sqlalchemy import Table, Column, Integer, String, ForeignKey
from sqlalchemy.orm import mapper

from webscard.utils import dbsession, metadata

def stringify(bytes):
    """
    >>> stringify([0,3, 66])
    '00 03 42'
    """
    def hexlikeiwant(b):
        """
        >>> hexlikeiwant(10)
        '0A'
        >>> hexlikeiwant(65)
        '41'
        """
        b = hex(b)[2:].upper()
        if len(b) == 1:
            b = '0' + b
        return b
    map(hexlikeiwant, bytes)
    return ' '.join(bytes)

apdu_table = Table('apdus', metadata,
    Column("uid", Integer, primary_key=True),
    Column("operation_uid", Integer, ForeignKey('operations.uid')),
    Column("type", Integer),
    Column("cla", Integer),
    Column("ins", Integer),
    Column("P1", Integer),
    Column("P2", Integer),
    Column("Le", Integer),
    Column("Lc", Integer),
    Column("data_command", String),
    Column("data_response", String),
    Column("SW1", Integer),
    Column("SW2", Integer),
)

class APDU(object):
    query = dbsession.query_property()

    def __init__(self, operation, bytes):
        self.operation_uid = operation.uid
        self.command = bytes
        dbsession.add(self)

    def received(self, bytes):
        response = bytes
        if (len(self.command) == 4) and (len(response) == 2):
            self.type = 1
            self.cla, self.ins, self.P1, self.P2 = self.command
            self.SW1, self.SW2 = response
        elif (len(self.command) == 5) and (len(response) == self.command[4] + 2):
            self.type = 2
            self.cla, self.ins, self.P1, self.P2, self.Le = self.command
            self.data_response = stringify(response[:-2])
            self.SW1, self.SW2 = response[-2:]
        elif (len (self.command) == self.command[4] + 5) and (len(response) == 2):
            self.type = 3
            self.cla, self.ins, self.P1, self.P2, self.Le = self.command[:5]
            self.data_command = stringify(self.command[5:])
            self.SW1, self.SW2 = response
        elif (len (self.command) == self.command[4] + 6) and (len(response) == self.command[:-1] + 2):
            self.type = 4
            self.cla, self.ins, self.P1, self.P2, self.Le = self.command[:5]
            self.data_command = stringify(self.command[5:])
            self.data_response = stringify(response[:-2])
            self.SW1, self.SW2 = response[-2:]
        else:
            self.type = 0
            self.data_command = stringify(self.command)
            self.data_response = stringify(response)

mapper(APDU, apdu_table)
