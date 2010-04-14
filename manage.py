#!/usr/bin/env python
from werkzeug import script

from webscard.config import Config

CONFIG_FILE = 'webscard.cfg'

config = Config(CONFIG_FILE)

def make_app():
    from webscard.application import WebSCard
    return WebSCard(config)

def make_shell():
    application = make_app()
    return locals()

action_runserver = script.make_runserver(
    make_app, hostname=config.gethost(),
    port=config.getport(),
    use_reloader=True, extra_files=CONFIG_FILE, use_debugger=True)
action_initdb = lambda: make_app().init_database()
action_shell = script.make_shell(make_shell)

script.run()
