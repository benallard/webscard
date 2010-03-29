from werkzeug import BaseRequest, cached_property
from werkzeug.contrib.securecookie import SecureCookie

from webscard.utils import application

class Request(BaseRequest):

    def __init__(self, environ, **kw):
        BaseRequest.__init__(self, environ, kw)
        self.secret_key = application.config.getstring('cookies.secret', application.random_key)
    
    @cached_property
    def client_session(self):
        data = self.cookies.get('session_data')
        if not data:
            return SecureCookie(secret_key=self.secret_key)
        return SecureCookie.unserialize(data, self.secret_key)
