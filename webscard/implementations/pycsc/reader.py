class Reader(object):
    name = "PyC/SC Reader 0"
    def __init__(self, name, config):
        self.protocol = config.getinteger('%s.protocol' % name, 2)
