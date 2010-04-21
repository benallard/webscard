from distutils.core import setup
import py2exe

packages= ['webscard', 'webscard.models', 
           'webscard.implementations', 'webscard.icon']

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

setup(
    name='WebSCard',
    version='0.5',
    url='http://bitbucket.org/benallard/webscard',
    packages=packages,
    requires=['werkzeug', 'sqlalchemy', 'pybonjour', 'elementtree'],
    console=['manage.py'],#, 'winservice.py'],
    windows=['start_qt.py'],
    service=[myservice],
    data_files=[('', ['Spider.web.logo.png', 'sample.cfg'])],
    options={'py2exe': {
            "packages":["sqlalchemy.dialects.sqlite", "sip", "pybonjour",],
            "excludes":["Tkconstants", "tcl", "Tkinter"],
}})
