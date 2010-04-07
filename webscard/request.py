from werkzeug import BaseRequest, cached_property
from werkzeug.contrib.securecookie import SecureCookie

from webscard.utils import application, render
from webscard.models.session import Session


class Request(BaseRequest):
    
    @cached_property
    def client_session(self):
        data = self.cookies.get('session_data')
        if not data:
            return SecureCookie(secret_key=application.secret_key)
        return SecureCookie.unserialize(data, application.secret_key)

    def getsession(self):
        session_data = self.client_session
	if ('sid' in session_data) and (session_data['sid'] is not None):
            self.session = Session.query.get(session_data['sid'])
        else:
            print "---------------------------new session !"
            self.session = Session()

    @property
    def shouldsavesession(self):
        return self.session.shouldsave

    @cached_property
    def implementation(self):
        return self.session.implementation

    def storesession(self):
        self.session.store()
        self.client_session['sid'] = self.session.uid

    def validatesession(self, **values):
        if 'context' in values:
            res = self.session.validatecontext(values['context'])
        elif 'card' in values:
            res = self.session.validatehandle(values['card'])
        else:
            res = None
        if res is not None:
            print "bad session"
            return render(self, res)
        print "good session"
        return None
