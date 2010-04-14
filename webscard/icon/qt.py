import sys

from PyQt4.QtGui import (QApplication, QSystemTrayIcon, QAction, QMenu, QIcon, QPixmap)
from PyQt4.QtCore import (Qt, QString, QThread)

from webscard.application import WebSCard
from webscard.config import Config

import werkzeug
from werkzeug import run_simple

class WebServerThread(QThread):
    def __init__(self, config):
        QThread.__init__(self)
        self.config = config
        self.wscard = WebSCard(config)
        self.app = werkzeug._easteregg(self.wscard)

    def run(self):
        run_simple(self.config.getstring('web.host', '0.0.0.0'),
                   self.config.getinteger('web.port', 3333),
                   self.app)
        

class WebSCardTrayIcon(QSystemTrayIcon):
    def __init__(self, config):
        QSystemTrayIcon.__init__(self)
        self.setIcon(QIcon(QPixmap('Z:\\Spider.web.logo.png')))
        self.menu = QMenu(QString("WebScard Menu"))
        self.setContextMenu(self.menu)

        # -- reload

        # -- configure with GUI

        # -- initdb
        action = QAction(QString(u'Init db'), self)
        action.setToolTip(u'Initialize the database where is is configured')
        action.triggered.connect(self.on_initdb)
        self.menu.addAction(action)

        # -- Quit
        action = QAction(QString(u'Quit'), self)
        action.setToolTip(u'Quit everything')
        action.triggered.connect(self.on_quit)
        self.menu.addAction(action)

        self.setToolTip(QString(u'WebSCard: Smart card WSGI server'))

        self.webserverthread = WebServerThread(config)
        self.webserverthread.start()

        self.show()

    def on_initdb(self):
        self.webserverthread.wscard.init_database()

    def on_quit(self):
        """ Callback to quit """
        self.hide()
        self.menu.destroy()
        global app
        app.quit()

def make_app(config_path):
    config = Config(config_path)
    try:
        global app
        app = QApplication(sys.argv)
        QApplication.setQuitOnLastWindowClosed(False)
        status_icon = WebSCardTrayIcon(config)
        app.exec_()
    except KeyboardInterrupt:
        pass
    
if __name__ == "__main__":
    make_app('z:\\WSCenv\\webscard\\webscard.cfg')
