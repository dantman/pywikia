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
import re, os

import wikipedia

class Exceptions(object):
    def __init__(self):
        self.d={}

    def add(self, one, two):
        try:
            self.d[one].append(two)
        except KeyError:
            self.d[one] = [two]

    def check(self, one, two):
        try:
            return two in self.d[one]
        except KeyError:
            return False
        
_bigger = Exceptions()
_unequal = Exceptions()

def read_exceptions():
    Re = re.compile(r' *\[\[(.*)\]\] *([^ ]+) *\[\[(.*)\]\]')
    fn = '%s-exceptions.dat' % repr(wikipedia.getSite())
    if not os.path.exists(fn):
        fn = '%s-exceptions.dat' % wikipedia.getSite().lang
    try:
        f = open(fn)
    except IOError:
        pass
    else:
        for line in f:
            m = Re.match(line)
            if not m:
                raise ValueError("Do not understand %s"%line)
            code, name = m.group(1).split(':',1)
            pl1 = wikipedia.Page(wikipedia.getSite(code=code), name)
            code, name = m.group(3).split(':',1)
            pl2 = wikipedia.Page(wikipedia.getSite(code=code), name)
            if m.group(2) == '<':
                _bigger.add(pl1, pl2)
            elif m.group(2) == '!=':
                _unequal.add(pl1, pl2)
            else:
                raise ValueError("Do not understand operator %s"%line)

bigger = _bigger.check

unequal = _unequal.check
