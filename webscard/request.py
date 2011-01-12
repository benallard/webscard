import elementtree.ElementTree as ET

from xml.parsers.expat import ExpatError

from werkzeug import BaseRequest, CommonRequestDescriptorsMixin, AcceptMixin
from werkzeug import cached_property
from werkzeug.contrib.securecookie import SecureCookie

from webscard.render import render
from webscard.utils import application
from webscard.models.session import Session

from webscard.implementations import chooser

from webscard import soap

COOKIENAME = 'session_data'

class Request(BaseRequest, CommonRequestDescriptorsMixin, AcceptMixin):

    max_content_length = 1024 * 1024 # 1 MB

    newsession = False

    def __init__(self, environ, **kw):
        BaseRequest.__init__(self, environ, kw)
        self.getsession()
        self.implementation = chooser.get(self.session)

    @cached_property
    def client_session(self):
        data = self.cookies.get(COOKIENAME)
        if not data:
            return SecureCookie(secret_key=application.secret_key)
        return SecureCookie.unserialize(data, application.secret_key)

    def getsession(self):
        session_data = self.client_session
        session = None
        if ('sid' in session_data) and (session_data['sid'] is not None):
            session = Session.query.get(session_data['sid'])
            if session.closedby is not None:
                # session expired ...
                session = None
            else:
                session.update()

        if session is None:
            print "---------------------------new session !"
            session = Session(self)
            chooser.acquire(session)
            self.newsession = True
        else:
            print "using session %d" % session.uid

        self.session = session 

    def storesession(self, response):
        if self.newsession:
            self.client_session['sid'] = self.session.uid
            session_data = self.client_session.serialize()
            response.set_cookie(COOKIENAME, session_data)

    def validatesession(self, **values):
        if 'context' in values:
            self.context = values['context']
            res = self.session.validatecontext(values['context'])
        elif 'card' in values:
            self.card = values['card']
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
            print "Wrong headers: %s" % self.headers.get('content-type')

    @cached_property
    def soapbody(self):
        elem = self.xmlroot
        if elem.tag == '{http://www.w3.org/2001/12/soap-envelope}Envelope':
            elem = elem.find('{http://www.w3.org/2001/12/soap-envelope}Body')
            if (elem is not None) and (len(elem) == 1):
                return elem.getchildren()[0]
            return None
        return elem
                

MACROS = ["""
<operations>
  <operation name="establishcontext" />
  <operation name="connect" readername="OmniKey CardMan 6121 00 00" />
  <operation name="transmit">
    <byte base="16">00</byte><byte>164</byte><byte>4</byte><byte>0</byte>
    <byte>8</byte><byte>160</byte><byte>0</byte><byte>0</byte><byte>0</byte>
    <byte>3</byte><byte>0</byte><byte>0</byte><byte>0</byte>
  </operation>
  <operation name="transmit">
    <byte>128</byte><byte>202</byte><byte>159</byte><byte>127</byte><byte>0</byte>
  </operation>
  <operation name="disconnect" />
  <operation name="releasecontext" />
</operations>""",
          """
<operations>
  <operation name="establishcontext" />
  <operation name="connect" readername="OMNIKEY CardMan 5x21-CL 0" />
  <operation name="transmit" ignorefailure="1">
    <byte base="16">FF</byte><byte base="16">CA</byte><byte>0</byte>
    <byte>0</byte><byte>0</byte>
  </operation>
  <operation name="disconnect" ignorefailure="1" />
  <operation name="releasecontext" ignorefailure="1" />
</operations>"""
]

class FileObj(object):
    def __init__(self, data):
        self.data = data
        self.index = 0
    def read(self, size):
        self.index += size
        return self.data[self.index-size:self.index]
