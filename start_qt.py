#!/usr/bin/env python

import os

from webscard.icon import qt
from webscard.utils import main_is_frozen, get_main_dir

if main_is_frozen():
    import sys
    sys.stderr = open('webscard_err.log', 'w')
    sys.stdout = open('webscard_out.log', 'w')

if __name__ == "__main__":
    qt.make_app(os.path.join(get_main_dir(),'webscard.cfg'))
