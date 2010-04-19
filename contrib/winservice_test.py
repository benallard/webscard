from winservice import Service, instart

class Test(Service):
    def start(self):
        self.runflag=True
        while self.runflag:
            self.sleep(10)
            self.log("I'm alive ...")
    def stop(self):
        self.runflag=False
        self.log("I'm done")

instart(Test, 'aTest', 'Python Service Test')
## end of http://code.activestate.com/recipes/551780/ }}}
