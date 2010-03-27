from werkzeug import BaseRequest, cached_property
from werkzeug.contrib.securecookie import SecureCookie

# need to make this a config element
SECRET_KEY = "abcd"

class Request(BaseRequest):
    
    @cached_property
    def client_session(self):
        data = self.cookies.get('session_data')
        if not data:
            return SecureCookie(secret_key=SECRET_KEY)
        return SecureCookie.unserialize(data, SECRET_KEY)
