from bbfreeze import Freezer

f = Freezer('bbfreeze', includes=["webscard.implementations.clusterscard", "sqlalchemy.dialects.sqlite"])
f.addScript('cherrypyserver.py')
f.addScript('manage.py')
f()
