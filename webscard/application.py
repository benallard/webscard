from sqlalchemy import create_engine
from werkzeug import ClosingIterator
from werkzeug.exceptions import NotFound
from werkzeug.wsgi import SharedDataMiddleware


from webscard.utils import dbsession, local, local_manager, metadata, url_map, get_static_dir
from webscard import views, bonjour

from webscard.models import handle, session, operation, apdu

from webscard.request import Request

from webscard.implementations import chooser

class WebSCard(object):

    def __init__(self, config):
        local.application = self
        self.config = config
        db_uri = self.config.getstring('db.uri', "sqlite:///webscard.db")
        self.database_engine = create_engine(
            db_uri, convert_unicode=True, 
            echo = config.getbool('logger.db', False))
        dbsession.configure(bind=self.database_engine)
        self.secret_key = config.getcookiesecret()
        chooser.initialize()
        bonjour.register(config.getport(), config.getimplementations())
        self.dispatch = SharedDataMiddleware(self.dispatch, {
            '/static': get_static_dir(),
        })
        if config.getbool('logger.profile', False):
            from repoze.profile.profiler import AccumulatingProfileMiddleware
            self.dispatch = AccumulatingProfileMiddleware(
                self.dispatch,
                log_filename='webscard.profile.log',
                cachegrind_filename='cachegrind.out.webscard'
                )

    def dispatch(self, environ, start_response):
        local.application = self
        request = Request(environ)
        local.url_adapter = url_map.bind_to_environ(environ)
        response = self.getresponse(request)
        return ClosingIterator(response(environ, start_response),
                               [dbsession.flush, dbsession.remove, 
                                local_manager.cleanup])

    def __call__(self, environ, start_response):
        return self.dispatch(environ, start_response)

    def getresponse(self, request):
        try:
            endpoint, values = local.url_adapter.match()
        except NotFound, expt:
            return expt

        request.endpoint = endpoint
        request.values = values
        handler = getattr(views, endpoint)
        response = None
        if self.config.getbool('internal.sessioncheck', True):
            response = request.validatesession(**values)
        if response is None:
            response = handler(request, **values)

        request.storesession(response)
        return response

    def init_database(self):
        """ This create the database, Need to find a way to update it also """
        metadata.create_all(self.database_engine)
