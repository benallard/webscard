import os

from cherrypy import wsgiserver
from paste.translogger import TransLogger
from webscard.application import WebSCard

from webscard.config import Config
from webscard.utils import get_main_dir

config = Config(os.path.join(get_main_dir(), 'webscard.cfg'))

app = TransLogger(WebSCard(config))

server = wsgiserver.CherryPyWSGIServer((config.gethost(), config.getport()), app)
try:
    server.start()
except KeyboardInterrupt:
    server.stop()
