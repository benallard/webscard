#!/usr/bin/env python

from webscard.icon import qt
from webscard.utils import main_is_frozen

if main_is_frozen():
    import sys
    sys.stderr = open('webscard_err.log', 'w')
    sys.stdout = open('webscard_out.log', 'w')

if __name__ == "__main__":
    qt.make_app('webscard.cfg')
