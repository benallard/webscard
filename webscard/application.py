import string
import random

from sqlalchemy import create_engine
from werkzeug import ClosingIterator
from werkzeug.exceptions import HTTPException


from webscard.utils import dbsession, local, local_manager, metadata ,url_map
from webscard import views

from webscard.models import handle, session
from webscard.models.session import Session

from webscard.request import Request

from webscard import implementations

class WebSCard(object):

    def __init__(self, config):
        local.application = self
        self.config = config
        db_uri = self.config.getstring('db.uri', "sqlite:///:memory")
        self.database_engine = create_engine(db_uri, convert_unicode=True)
        if db_uri == "sqlite:///:memory":
            self.init_database()
        dbsession.configure(bind=self.database_engine)
        self.random_key = "".join([random.choice(string.letters)
                                    for i in range(20)])

    def __call__(self, environ, start_response):
        local.application = self
        request = Request(environ)
        local.url_adapter = url_map.bind_to_environ(environ)
        response = self.getresponse(request)
        return ClosingIterator(response(environ, start_response),
                               [dbsession.remove, local_manager.cleanup])

    def getresponse(self, request):
        session_data = request.client_session
	if ('sid' in session_data) and (session_data['sid'] is not None):
            session = Session.query.get(session_data['sid'])
        else:
            print "---------------------------new session !"
            session = Session(implementations.getone())
        endpoint, values = local.url_adapter.match()
        handler = getattr(views, endpoint)

        try:
            response = handler(request, session, **values)
        except HTTPException, e:
            return e
        
        if session.shouldsave:
            session.store()
            request.client_session['sid'] = session.uid
            session_data = request.client_session.serialize()
            response.set_cookie('session_data', session_data)
        return response

    def init_database(self):
        metadata.create_all(self.database_engine)
