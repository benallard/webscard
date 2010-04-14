import elementtree.ElementTree as ET

from werkzeug import BaseRequest, cached_property
from werkzeug.contrib.securecookie import SecureCookie

from webscard.utils import application, render
from webscard.models.session import Session

cookiename = 'session_data'

class Request(BaseRequest):

    max_content_length = 1024 * 1024 # 1 MB

    newsession = False

    def __init__(self, environ, **kw):
        BaseRequest.__init__(self, environ, kw)
        self.getsession()

    @cached_property
    def client_session(self):
        data = self.cookies.get(cookiename)
        if not data:
            print "No cookie"
            return SecureCookie(secret_key=application.secret_key)
        return SecureCookie.unserialize(data, application.secret_key)

    def getsession(self):
        session_data = self.client_session
	if ('sid' in session_data) and (session_data['sid'] is not None):
            self.session = Session.query.get(session_data['sid'])
            self.session.update()
        else:
            print "---------------------------new session !"
            self.session = Session(self)
            self.newsession = True

    @cached_property
    def implementation(self):
        return self.session.implementation

    def storesession(self, response):
        if self.newsession:
            self.client_session['sid'] = self.session.uid
            session_data = self.client_session.serialize()
            response.set_cookie(cookiename, session_data)

    def validatesession(self, **values):
        if 'context' in values:
            res = self.session.validatecontext(values['context'])
        elif 'card' in values:
            res = self.session.validatehandle(values['card'])
        else:
            res = None
        if res is not None:
            return render(self, res)
        return None

    @cached_property
    def xmlroot(self):
        if application.config.getbool('internal.debug', False):
             tree = ET.ElementTree(file=FileObj('<root><operation name="establishcontext" /><operation name="connect" readername="OmniKey CardMan 6121 00 00" /><operation name="transmit"><cmd>0</cmd><cmd>164</cmd><cmd>4</cmd><cmd>0</cmd><cmd>8</cmd><cmd>160</cmd><cmd>0</cmd><cmd>0</cmd><cmd>0</cmd><cmd>3</cmd><cmd>0</cmd><cmd>0</cmd><cmd>0</cmd></operation><operation name="transmit"><cmd>128</cmd><cmd>202</cmd><cmd>159</cmd><cmd>127</cmd><cmd>0</cmd></operation><operation name="disconnect" /><operation name="releasecontext" /></root>'))
             return tree.getroot()
        if self.headers.get('content-type') == 'application/soap+xml':
            tree = ET.ElementTree(file=FileObj(self.data))
            return tree.getroot()
       

class FileObj(object):
    def __init__(self, data):
        self.data = data

    index = 0
    def read(self, size):
        self.index += size
        return self.data[self.index-size:self.index]
