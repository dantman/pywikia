"""Some pages contain "bigger" subjects than others. To be able to allow
   pages to contain interwiki links to bigger pages without requesting backlinks
   and without following all interwiki links from the bigger page, this module
   contains some helper code"""
#
# (C) Rob W.W. Hooft, 2003
#
# Distribute under the terms of the PSF license.
#
__version__ = '$Id$'
#
import re

import wikipedia

exceptions = []

def read_exceptions():
    Re = re.compile(r'\[\[(.*)\]\] *< *\[\[(.*)\]\]')
    try:
        f = open('%s-exceptions.dat' % wikipedia.mylang)
    except IOError:
        pass
    else:
        for line in f:
            m = Re.match(line)
            if not m:
                raise ValueError("Do not understand %s"%line)
            exceptions.append((m.group(1),m.group(2)))

def bigger(inpl, pl):
    if pl.hashname():
        # If we refer to part of the page, it is bigger
        return True
    x1 = str(inpl)
    x2 = str(pl)
    for small,big in exceptions:
        if small == x1 and big == x2:
            return True
    return False
