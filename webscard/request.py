import elementtree.ElementTree as ET

from werkzeug import BaseRequest, CommonRequestDescriptorsMixin, AcceptMixin
from werkzeug import cached_property
from werkzeug.contrib.securecookie import SecureCookie

from webscard.utils import application, render
from webscard.models.session import Session

from webscard import soap

cookiename = 'session_data'

class Request(BaseRequest, CommonRequestDescriptorsMixin, AcceptMixin):

    max_content_length = 1024 * 1024 # 1 MB

    newsession = False

    def __init__(self, environ, **kw):
        BaseRequest.__init__(self, environ, kw)
        self.getsession()

    @cached_property
    def client_session(self):
        data = self.cookies.get(cookiename)
        if not data:
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
            tree = ET.ElementTree(file=FileObj(soap.SUGAR % MACROS[1]))
            print tree
            return tree.getroot()
        if self.mimetype in ['application/soap+xml', 
                             'text/xml']:
            try:
                tree = ET.ElementTree(file=FileObj(self.data))
                return tree.getroot()
            except ExpatError:
                print "Wrong XML"
                return None
        else:
            print "Wong headers: %s" % self.headers.get('content-type')

    @cached_property
    def soapbody(self):
        elem = self.xmlroot
        if elem.tag == '{http://www.w3.org/2001/12/soap-envelope}Envelope':
            elem = elem.find('{http://www.w3.org/2001/12/soap-envelope}Body')
            if (elem is not None) and (len(elem) == 1):
                return elem.getchildren()[0]
            return None
        return elem
                

MACROS = ['<operations><operation name="establishcontext" /><operation name="connect" readername="OmniKey CardMan 6121 00 00" /><operation name="transmit"><cmd>0</cmd><cmd>164</cmd><cmd>4</cmd><cmd>0</cmd><cmd>8</cmd><cmd>160</cmd><cmd>0</cmd><cmd>0</cmd><cmd>0</cmd><cmd>3</cmd><cmd>0</cmd><cmd>0</cmd><cmd>0</cmd></operation><operation name="transmit"><cmd>128</cmd><cmd>202</cmd><cmd>159</cmd><cmd>127</cmd><cmd>0</cmd></operation><operation name="disconnect" /><operation name="releasecontext" /></operations>', 
          '<operations><operation name="establishcontext" /><operation name="connect" readername="OMNIKEY CardMan 5x21-CL 0" /><operation name="transmit" ignorefailure="1"><byte>255</byte><byte>202</byte><byte>0</byte><byte>0</byte><byte>0</byte></operation><operation name="disconnect" ignorefailure="1" /><operation name="releasecontext" ignorefailure="1" /></operations>']

class FileObj(object):
    def __init__(self, data):
        self.data = data

    index = 0
    def read(self, size):
        self.index += size
        return self.data[self.index-size:self.index]
