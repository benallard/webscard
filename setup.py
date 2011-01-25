import os

from distutils.core import setup
import py2exe

packages= ['webscard', 'webscard.models', 'webscard.bonjour',
           'webscard.bonjour.zc', 'webscard.implementations', 'webscard.icon',
           'webscard.implementations.pycsc',]

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

def data_files(name, extension=""):
    root = os.path.join('webscard',name)
    dirList=os.listdir(root)
    templist = []
    for path in dirList:
        if path.endswith(extension):
            templist.append(os.path.join(root,path))
    return (name, templist)

setup(
    name='WebSCard',
    version='0.5',
    url='http://bitbucket.org/benallard/webscard',
    packages=packages,
    requires=['werkzeug', 'sqlalchemy', 'pybonjour', 'elementtree', 'cherrypy', 'jinja2', 'pythoncard', 'python', 'pythoncardx', 'paste'],
    console=['manage.py','cherrypyserver.py'],
    windows=['start_qt.py'],
    service=[myservice],
    data_files=[('', ['Spider.web.logo.png', 'sample.cfg']),
                data_files('templates', '.html'),
                data_files('static')],
    options={'py2exe': {
            "packages":["sqlalchemy.dialects.sqlite", "pybonjour",
                        "webscard.implementations.empty", 
                        "webscard.implementations.clusterscard"],
            "excludes":["Tkconstants", "tcl", "Tkinter"],
}})
