#!/usr/bin/env python
from werkzeug import script

def make_app():
    from webscard.application import WebSCard
    from webscard.config import Config
    return WebSCard(Config("webscard.cfg"))

def make_shell():
    application = make_app()
    return locals()

action_runserver = script.make_runserver(
    make_app, hostname='0.0.0.0', port=3333, use_reloader=True, extra_files="webscard.cfg", use_debugger=True)
action_initdb = lambda: make_app().init_database()
action_shell = script.make_shell(make_shell)

script.run()
