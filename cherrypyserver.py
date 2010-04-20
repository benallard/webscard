from cherrypy import wsgiserver
from webscard.application import WebSCard

from webscard.config import Config

config = Config('webscard.cfg')

server = wsgiserver.CherryPyWSGIServer((config.gethost(), config.getport()), WebSCard(config))
try:
    server.start()
except KeyboardInterrupt:
    server.stop()
