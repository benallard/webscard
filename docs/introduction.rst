Introduction
============

Overview
--------

WebSCard acts as a universal smartcard proxy.

Ouh! That's a lot of weird words at once let's try to make them a bit
more kind:

smartcard
   Those are those plastic pieces with a chip on it everyone has in
   his wallet, they use to call Banking card for instance.

proxy
   A proxy allow you to get some content from some place without even
   needing to get there. That's what WebSCard enable to you w.r.t
   smartcards. It allows you to access a smartcard without needing
   one.

universal
   WebSCard has been written with expendablity and interopability as
   one of its first goals. Through it you can access as well as a real
   smartcard located three block further, or even a piece of software
   pretending to be your smartcard on the server itself.

Motivation
----------

Servers are powerfull. unfortunately, they don't play really well with
hardware. As we just saw, smartcards are pieces of hardware. it is
thus difficult to run some software one those servers that needs
them. This is the main reason why WebSCard is born. the second one
being the possibility to test some software without actually needing a
real smartcard.

Features
--------

* It is :ref:`session` aware.
* It logs everything in a :ref:`DB`
* It can be :ref:`configured`.
* It supports :ref:`multiple implementations`.
* It supports :ref:`Bonjour`
* It supports :ref:`SOAP`

