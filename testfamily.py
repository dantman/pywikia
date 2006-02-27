#!/usr/bin/python
# -*- coding: utf-8	 -*-
"""
This utility's primary use is to find all mismatches between the namespace
naming in the family files and the language files on the wiki servers.

If the -all parameter is used, it runs through all known languages in a family.

Examples:
    
    python testfamily.py -family:wiktionary -lang:en
    
    python testfamily.py -family:wikipedia -all -log:logfilename.txt 

"""
#
# (C) Yuri Astrakhan, 2005
#
# Distributed under the terms of the MIT license.
#
__version__ = '$Id$'
#

import sys, wikipedia, traceback


#===========

def testSite(site):
    try:
        
        wikipedia.getall(site, [wikipedia.Page(site, 'Any page name')])
    except KeyboardInterrupt:
        raise
    except:
        wikipedia.output( u'Error processing language %s' % site.lang )
        wikipedia.output( u''.join(traceback.format_exception(*sys.exc_info())))
    

def main():
    all = False
    for arg in sys.argv[1:]:
        arg = wikipedia.argHandler(arg, 'testfamily')
        if arg:
            if arg == '-all':
                all = True
    
    mySite = wikipedia.getSite()
    fam = mySite.family

    if all:
        for lang in fam.knownlanguages:
            testSite(wikipedia.getSite(lang))
    else:
        testSite(mySite)
                     
    if False:
        # skip until the family gets global fixing
        
        wikipedia.output(u"\n\n------------------ namespace table -------------------\n");

        wikipedia.output(u"		   self.namespaces = {")
        for k,v in sorted(fam.namespaces.iteritems()):
            wikipedia.output(u"			   %i: {" % k)
            for k2,v2 in sorted(v.iteritems()):
                if v2 is not None:
                    v2 = u"u'%s'" % v2
                wikipedia.output(u"				   '%s': %s," % (k2,v2))
            wikipedia.output(u"			   },")
        wikipedia.output(u"		   }")

if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()
