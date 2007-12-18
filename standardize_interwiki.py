#!/usr/bin/python
# -*- coding: utf-8  -*-
"""
Loop over all pages in the home wiki, standardizing the interwiki links.
 
Parameters:
 
-start:     - Set from what page you want to start
"""
#
# (C) Rob W.W. Hooft, 2003
# (C) Filnik, 2007
#
# Distributed under the terms of the MIT license.
#
__version__='$Id$'
#
 
import os, sys
import wikipedia, config
import difflib
 
# The summary that the Bot will use.
comment = {
    'de':u'Bot: Interwikilinks standardisieren',
    'en':u'Robot: interwiki standardization',
    'he':u'בוט: מסדר את האינטרוויקי',
    'no':u'bot: Språklenkestandardisering',
    'it':u'Bot: Standardizzo interwiki',
    'ksh':u'Bot: Engerwiki Lengks opprüühme',
    'nds':u'Bot: Links twüschen Wikis standardisseern',
    }
site = wikipedia.getSite()
comm = wikipedia.translate(site, comment)
 
# Some parameters
options = list()
start = list()
filelist = list()
hints = {}
debug = 0
start = '!'
nothing = False
 
# Load the default parameters and start
for arg in wikipedia.handleArgs():
    if arg.startswith('-start'):
        if len(arg) == 6:
            start = str(wikipedia.input(u'From what page do you want to start?'))
        else:
            start = str(arg[7:])

# What follows is the main part of the code.
try:
    for pl in site.allpages(start):
        plname = pl.title()
        wikipedia.output(u'\nLoading %s...' % plname)
        try:
            oldtext = pl.get()
        except wikipedia.IsRedirectPage:
            wikipedia.output(u"%s is a redirect!" % plname)
            continue
        old = pl.interwiki()
        new = {}
        for pl2 in old:
            new[pl2.site()] = pl2
        newtext = wikipedia.replaceLanguageLinks(oldtext, new)
        if new:
            if oldtext != newtext:
                wikipedia.showDiff(oldtext, newtext)
                # Submit changes
                try:
                    status, reason, data = pl.put(newtext, comment=comm)
                    if str(status) != '302':
                        wikipedia.output(status, reason)
                except wikipedia.LockedPage:
                    wikipedia.output(u"%s is locked" % plname)
                    continue
            else:
                wikipedia.output(u'No changes needed.')
                continue
        else:
            wikipedia.output(u'No interwiki found.')
            continue
finally:
    wikipedia.stopme()
