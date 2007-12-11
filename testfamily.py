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
    language = None
    fam = None
    for arg in wikipedia.handleArgs():
        if arg == '-all':
            all = True
        elif arg[0:7] == '-langs:':
            language = arg[7:]
        elif arg[0:10] == '-families:':
            family = arg[10:]

    mySite = wikipedia.getSite()
    if language is None:
        language = mySite.lang
    if fam is None:
        fam = mySite.family.name

    families = fam.split(',')
    for family in families:
        try:
            fam = wikipedia.Family(family)
        except ValueError:
            wikipedia.output(u'No such family %s' % family)
            continue
        if all:
            for lang in fam.langs.iterkeys():
                testSite(wikipedia.getSite(lang, family))
        else:
            languages = language.split(',')
            for lang in languages:
                testSite(wikipedia.getSite(lang, family))

if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()
