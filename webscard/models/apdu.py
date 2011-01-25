from sqlalchemy import Table, Column, Integer, Text, ForeignKey
from sqlalchemy.orm import mapper

from webscard.utils import dbsession, metadata, stringify

apdu_table = Table('apdus', metadata,
    Column("uid", Integer, primary_key=True),
    Column("type", Integer),
    Column("cla", Integer),
    Column("ins", Integer),
    Column("P1", Integer),
    Column("P2", Integer),
    Column("Le", Integer),
    Column("Lc", Integer),
    Column("data_command", Text),
    Column("data_response", Text),
    Column("SW1", Integer),
    Column("SW2", Integer),
)

class APDU(object):
    query = dbsession.query_property()

    def __init__(self, bytesarr):
        self.command = bytesarr
        dbsession.add(self)
        dbsession.flush()

    def received(self, bytesarr):
        response = bytesarr

        if len(self.command) < 4:
            self.type = 0
            self.cla, self.ins, self.P1, self.P2 = (self.command + [None, None, None, None])[:4]
            
        if len(self.command) == 4:
            self.type = 1
            self.Lc = 0
            self.Le = 0
            self.cla, self.ins, self.P1, self.P2 = self.command
            
        elif (len(self.command) == 5) or ((self.command[4] == 0) and (len(self.command) == 7)):
            self.type = 2
            self.cla, self.ins, self.P1, self.P2 = self.command[:4]
            self.Lc = 0
            self.Le, lelength = self.getLe()
            
        elif len(self.command) == (self.getLc()[0] + 5):
            self.type = 3
            self.cla, self.ins, self.P1, self.P2 = self.command[:4]
            self.Lc, lclength = self.getLc()
            self.data_command = stringify(self.command[4+lclength:])
            self.Le = 0

        else:
            self.type = 4
            self.cla, self.ins, self.P1, self.P2 = self.command[:4]
            self.Lc, lclength = self.getLc()
            self.Le, lelength = self.getLe()
            self.data_command = stringify(self.command[4+lclength:-lelength])

            
        self.data_response = stringify(response[:-2])
        self.SW1, self.SW2 = (response[-2:] + [None, None])[:2]

    def getLc(self):
        """ return a tuple (value, length of value) """
        if self.command[4] != 0:
            return self.command[4], 1
        else:
            return self.command[5] * 256 + self.command[6], 3

    def getLe(self):
        """
        return a tuple (value, length of value)
        asumption: there is an Lc
        """
        length = len(self.command) - 1
        if self.command[length] == 0:
            # last byte is a 00
            if self.command[4] == 0:
                # Lc is extended thus Le is extended
                if self.command[length-1] == 0:
                    return 65536, 2
                else:
                    return self.command[length-1] * 256, 2
            else:
                return 256, 1
        else:
            if self.command[4] == 0:
                return self.command[length-1] * 256 + self.command[length], 2
            return self.command[length], 1

mapper(APDU, apdu_table)
