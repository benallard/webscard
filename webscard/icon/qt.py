import sys

from PyQt4.QtGui import (QApplication, QSystemTrayIcon, QAction, QMenu, QIcon, QPixmap)
from PyQt4.QtCore import (Qt, QString)

class WebSCardTrayIcon(QSystemTrayIcon):
    def __init__(self):
        QSystemTrayIcon.__init__(self)
        self.setIcon(QIcon(QPixmap('Z:\\Spider.web.logo.png')))
        self.menu = QMenu(QString("WebScard Menu"))
        self.setContextMenu(self.menu)

        action = QAction(QString(u'&Quit'), self)
        action.setShortcut(Qt.CTRL + Qt.Key_Q)
        action.setToolTip(u'Quit everything')
        action.triggered.connect(self.on_quit)
        self.menu.addAction(action)

        self.setToolTip(QString(u'Click this icon to interact with'
                                u' WebSCard.'))
   
        self.show()

    def on_quit(self):
        """ Callback to quit """
        self.hide()
        self.menu.destroy()
        global app
        app.quit()

if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        QApplication.setQuitOnLastWindowClosed(False)
        status_icon = WebSCardTrayIcon()
        app.exec_()
    except KeyboardInterrupt:
        app.quit()
