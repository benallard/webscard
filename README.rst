########
WebSCard
########

Overview
========

This is a web application acting as a universal smartcard proxy : it provides a web interface to a smartcard, together with detailled logs about the communication passing by.

One of the goals is to allow testing of software which necessitate a smartcard from a computer without a readers.

It is meant to support different implementations of smartcards:

* Software emulations of javacards applets (via pycsc and pythoncard for instance)
* or real smartcards (via pyscard in this case).

Application
===========

WSGI Application
----------------

You can run it as a standalone Python `cherrypy`_ server, or as `werkzeug`_ server, or embed it inside `apache`_ / `IIS`_ / `Lighttpd`_ / `nginx`_ / ...

I recommend `cherrypy`_ for stable deployment (unless you already have a web server running) and werkzeug for development, `werkzeug`_ debugger is really worth mentioning, serving you a python shell at every level of the stacktrace in your browser.

Qt status bar launcher
----------------------

An idea I took from the `Hatta wiki`_, you can have a status bar icon to configure, launch, stop, ... WebSCard.

NT Service
----------

The application can also be configured as NT service, in this case, `cherrypy`_ will handle the requests.

Lua client
----------

For the sake of testing, a `lua`_ client is included. It depends on `luacurl`_. Source is in ``luaclient/client.lua``.

Features
========

* It is session aware.
* It logs everything in a DB
* It can be configured.
* It supports multiple implementations.
* It supports `Bonjour`_
* It supports `SOAP`_

Dependencies
============

WebSCard depends on the following packages:

* `Python`_: Tested on 2.5 and 2.6. Take it from your distribution (cygwin won't play well if you want to play with real hardware as there is not PCSC bridge available)
* `Werkzeug`_: The network layer is done by werkzeug
* `pyscard`_: This is an optional dependency if you don't want to play with real hardware.
* `SQLAlchemy`_: This is how the DB stuff is done.
* `elementTree`_: For XML parsing for SOAP.
* `Jinja2`_: For HTML templating.

.. note:: As pyscard requires compiling/swiging, ... I recommand installing it system-wide with the download from sourceforge.

Howto install the dependencies:
-------------------------------

You have three solutions:

#. Create a `virtualenv`_ and install everything in there.
#. Clone locally the repositories, and symlink/copy (depending on your platform) their package root directory in the WebSCard root directory such that an ``import X`` from WebSCard source code works fine.
#. Install system-wide

.. _`cherrypy`: http://www.cherrypy.org/
.. _`werkzeug`: http://werkzeug.pocoo.org/
.. _`apache`: http://www.apache.org/
.. _`IIS`: http://www.iis.net/
.. _`lighttpd`: http://www.lighttpd.net/
.. _`nginx`: http://nginx.net/
.. _`Hatta wiki`: http://hatta-wiki.org/
.. _`lua`: http://www.lua.org/
.. _`luacurl`: http://luacurl.luaforge.net/
.. _`Bonjour`: http://www.apple.com/support/bonjour/
.. _`SOAP`: http://en.wikipedia.org/wiki/SOAP
.. _`Python`: http://www.python.org/
.. _`pyscard`: http://pyscard.sourceforge.net/
.. _`SQLAlchemy`: http://www.sqlalchemy.org/
.. _`elementTree`: http://effbot.org/zone/element-index.htm
.. _`Jinja2`: http://jinja.pocoo.org/docs/
.. _`virtualenv`: http://www.virtualenv.org/en/latest/index.html
