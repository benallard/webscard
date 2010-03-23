import random

class HandleFactory:
    
    def __init__(self):
        self.list = {}
        self.current = {}

    def getauniqueone(self, current, impl):
        res = current
        while res in self.list:
            res = random.randint(0,2**32 - 1)
        self.list[res] = impl
        self.current[res] = current
        return res

    def getimplfor(self, handle):
        return self.list[handle]

    def getreal(self, handle):
        return self.current[handle]
