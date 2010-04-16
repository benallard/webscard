from distutils.core import setup
import py2exe

packages= ['webscard', 'webscard.models', 'webscard.implementations', 'webscard.icon']

setup(
    name='WebSCard',
    version='0.5',
    url='http://bitbucket.org/benallard/webscard',
    packages=packages,
    requires=['werkzeug', 'sqlalchemy', 'pybonjour', 'elementtree'],
    console=['manage.py'],
    windows=['start_qt.py'],
    data_files=[('', ['Spider.web.logo.png', 'sample.cfg'])],
    options={'py2exe': {
            "packages":["sqlalchemy.dialects.sqlite", "sip", "pybonjour",],
            "excludes":["Tkconstants", "tcl", "Tkinter"],

}})
