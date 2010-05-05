class Token(object):
    def __init__(self, name, config):
        ATR = config.get(name, 'ATR')
        ATR = ATR.split()
        self.ATR = map(lambda x: int(x, 16), ATR)
