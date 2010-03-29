from werkzeug import Request, ClosingIterator
from werkzeug.exceptions import HTTPException

from sqlalchemy import create_engine

from webscard.utils import dbsession, local, local_manager, metadata ,url_map
from webscard import views

from webscard.models import handle

class WebSCard(object):

    def __init__(self):
        local.application = self
        self.database_engine = create_engine("sqlite:////tmp/webscard.db", convert_unicode=True)

    def __call__(self, environ, start_response):
        local.application = self
        request = Request(environ)
        local.url_adapter = adapter = url_map.bind_to_environ(environ)
        try:
            endpoint, values = adapter.match()
            handler = getattr(views, endpoint)
            response = handler(request, **values)
        except HTTPException, e:
            response = e
        return ClosingIterator(response(environ, start_response),
                               [dbsession.remove, local_manager.cleanup])

    def init_database(self):
        metadata.create_all(self.database_engine)
