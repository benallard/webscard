import os

from cherrypy import wsgiserver
from webscard.application import WebSCard

from webscard.config import Config
from webscard.utils import get_main_dir

config = Config(os.path.join(get_main_dir(), 'webscard.cfg'))

server = wsgiserver.CherryPyWSGIServer((config.gethost(), config.getport()), WebSCard(config))
try:
    server.start()
except KeyboardInterrupt:
    server.stop()
