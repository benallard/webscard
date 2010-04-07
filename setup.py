from distutils.core import setup
import py2exe

packages= ['webscard', 'webscard.models', 'webscard.implementations']

setup(
    name='WebSCard',
    version='0.5',
    url='http://bitbucket.org/benallard/webscard',
    packages=packages,
    console=['manage.py'],
    options={'py2exe': {
            "packages":["sqlalchemy.dialects.sqlite"]
}})
