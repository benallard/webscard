import string
import random

from sqlalchemy import create_engine
from werkzeug import ClosingIterator
from werkzeug.exceptions import NotFound


from webscard.utils import dbsession, local, local_manager, metadata ,url_map, Exception2JSON, render
from webscard import views, bonjour

from webscard.models import handle, session, operation, apdu

from webscard.request import Request

from webscard.implementations import chooser

class WebSCard(object):

    def __init__(self, config):
        local.application = self
        self.config = config
        db_uri = self.config.getstring('db.uri', "sqlite:///:memory:")
        self.database_engine = create_engine(db_uri, convert_unicode=True)
        dbsession.configure(bind=self.database_engine)
        if db_uri == "sqlite:///:memory:":
            print "init db"
            self.init_database()
        self.secret_key = config.getstring('cookies.secret', 
                                           "".join([random.choice(string.letters)
                                                    for i in range(20)]))
        chooser.initialize()
        bonjour.register(config.getport(), config.getimplementations())

    def __call__(self, environ, start_response):
        local.application = self
        request = Request(environ)
        local.url_adapter = url_map.bind_to_environ(environ)
        response = self.getresponse(request)
        dbsession.commit()
        return ClosingIterator(response(environ, start_response),
                               [dbsession.remove, local_manager.cleanup])

    def getresponse(self, request):
        try:
            endpoint, values = local.url_adapter.match()
        except NotFound, e:
            return e

        handler = getattr(views, endpoint)
        response = None
        if self.config.getbool('internal.sessioncheck', True):
            response = request.validatesession(**values)
        if response is None:
            response = handler(request, **values)

        request.storesession(response)
        return response

    def init_database(self):
        metadata.create_all(self.database_engine)
