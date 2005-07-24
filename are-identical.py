"""
Simple bot to check whether two pages with the same name on different language
'pedias have interwiki links to the same page on another language.

Call the script with 3 arguments:

   python are-identical.py lang1 lang2 name

The script will either print "Yes" and return exit code 0,
                    or print "No"  and return exit code 1.

It may raise exceptions on pages that disappeared or whatever. This is
a simple framework at least for the moment.
"""
#
# (C) Rob Hooft, 2005
#
# Distributed under the terms of the PSF license.
#
__version__='$Id$'
#
from __future__ import generators

import sys, wikipedia

class TwoPageGenerator:
    def __init__(self, lang1, lang2, name):
        self.lang1 = lang1
        self.lang2 = lang2
        self.name = name

    def __iter__(self):
        yield wikipedia.Page(wikipedia.getSite(self.lang1), self.name)
        yield wikipedia.Page(wikipedia.getSite(self.lang2), self.name)


class IdenticalRobot:
    def __init__(self, generator):
        self.generator = generator

    def run(self):
        arr = []
        for x in self.generator:
            arr.append(x)
        pg1 = arr[0]
        pg2 = arr[1]
        iw1 = pg1.interwiki()
        iw2 = pg2.interwiki()
        for iw in iw1:
            if iw in iw2:
                print "Yes"
                sys.exit(0)
        print "No"
        sys.exit(1)
        
def main():
    args = []
    for arg in sys.argv[1:]:
        arg = wikipedia.argHandler(arg, 'are-identical')
        if arg:
            args.append(arg)
    g = TwoPageGenerator(*args)
    r = IdenticalRobot(g)
    r.run()
    
try:
    main()
finally:
    wikipedia.stopme()
            
        
