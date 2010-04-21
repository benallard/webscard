"""
The most basic (working) CherryPy 3.1 Windows service possible.
Requires Mark Hammond's pywin32 package.
"""

from cherrypy import wsgiserver
import win32serviceutil
import win32service
import win32evtlogutil

from webscard.application import WebSCard
from webscard.config import Config

class WebSCardService(win32serviceutil.ServiceFramework):
    """NT Service."""
    
    _svc_name_ = "WebSCardService"
    _svc_display_name_ = "WebSCard Service"

    def log(self, msg):
        import servicemanager
        win32evtlogutil.ReportEvent(self._svc_name_,
                                    servicemanager.PYS_SERVICE_STARTED,
                                    0, # category
                                    servicemanager.EVENTLOG_INFORMATION_TYPE,
                                    (self._svc_name_, msg))
    def SvcDoRun(self):
        self.log('beginning start')
        config = Config(r'c:\webscard.cfg')
        app = WebSCard(config)
        self.server =  wsgiserver.CherryPyWSGIServer((config.gethost(), config.getport()), app)

        self.log('starting on : http://%s:%d' % (config.gethost(), config.getport()))
        self.server.start()
        
    def SvcStop(self):
        self.server.stop()
        self.log('stopped')

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(WebSCardService)
