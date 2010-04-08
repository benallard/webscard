#!/usr/bin/env python
from werkzeug import script

CONFIG_FILE = 'webscard.cfg'

def make_app():
    from webscard.application import WebSCard
    from webscard.config import Config
    return WebSCard(Config(CONFIG_FILE))

def make_shell():
    application = make_app()
    return locals()

action_runserver = script.make_runserver(
    make_app, hostname='0.0.0.0', port=3333, use_reloader=True, extra_files=CONFIG_FILE, use_debugger=True)
action_initdb = lambda: make_app().init_database()
action_shell = script.make_shell(make_shell)

script.run()
