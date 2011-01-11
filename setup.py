import os

from distutils.core import setup
import py2exe

packages= ['webscard', 'webscard.models', 'webscard.bonjour',
           'webscard.bonjour.zc', 'webscard.implementations', 'webscard.icon']

class Target:
    def __init__(self, **kw):
        self.__dict__.update(kw)
        # for the versioninfo resources
        self.version = "0.5.0"
        self.company_name = "No Company"
        self.copyright = "no copyright"
        self.name = "py2exe sample files"

myservice = Target(
    description = "WebSCard Service",
    modules = ['winservice'],
)

def templates_data_files():
    root = 'webscard/templates'
    dirList=os.listdir(root)
    templist = []
    for path in dirList:
        if path.endswith('.html'):
            templist.append(os.path.join(root,path))
    return ('templates', templist)

setup(
    name='WebSCard',
    version='0.5',
    url='http://bitbucket.org/benallard/webscard',
    packages=packages,
    requires=['werkzeug', 'sqlalchemy', 'pybonjour', 'elementtree', 'cherrypy'],
    console=['manage.py','cherrypyserver.py'],
    windows=['start_qt.py'],
    service=[myservice],
    data_files=[('', ['Spider.web.logo.png', 'sample.cfg']),
                templates_data_files()],
    options={'py2exe': {
            "packages":["sqlalchemy.dialects.sqlite", "pybonjour",],
            "excludes":["Tkconstants", "tcl", "Tkinter"],
}})
