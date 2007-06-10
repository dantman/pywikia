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
    'en':u'Robot: interwiki standardization',
    'it':u'Bot: Standardizzo interwiki',
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
 
# Function stolen from wikipedia.py and modified ad hoc by Filnik.
def Diff(oldtext, newtext):
    """
    Prints a string showing the differences between oldtext and newtext.
    The differences are highlighted (only on Unix systems) to show which
    changes were made.
    """
    # For information on difflib, see http://pydoc.org/2.3/difflib.html
    color = {
        '+': 10, # green
        '-': 12  # red
    }
    diff = u''
    colors = []
    # This will store the last line beginning with + or -.
    lastline = None
    # For testing purposes only: show original, uncolored diff
    #     for line in difflib.ndiff(oldtext.splitlines(), newtext.splitlines()):
    #         print line
    for line in difflib.ndiff(oldtext.splitlines(), newtext.splitlines()):
        if line.startswith('?'):
            # initialize color vector with None, which means default color
            lastcolors = [None for c in lastline]
            # colorize the + or - sign
            lastcolors[0] = color[lastline[0]]
            # colorize changed parts in red or green
            for i in range(min(len(line), len(lastline))):
                if line[i] != ' ':
                    lastcolors[i] = color[lastline[0]]
            diff += lastline + '\n'
            # append one None (default color) for the newline character
            colors += lastcolors + [None]
        elif lastline:
            diff += lastline + '\n'
            # colorize the + or - sign only
            lastcolors = [None for c in lastline]
            lastcolors[0] = color[lastline[0]]
            colors += lastcolors + [None]
        lastline = None
        if line[0] in ('+', '-'):
            lastline = line
    # there might be one + or - line left that wasn't followed by a ? line.
    if lastline:
        diff += lastline + '\n'
        # colorize the + or - sign only
        lastcolors = [None for c in lastline]
        lastcolors[0] = color[lastline[0]]
        colors += lastcolors + [None]
    return (diff, colors)
 
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
                # Display the diff
                data = Diff(oldtext, newtext)
                diff = data[0]
                colors = data[1]
                if diff == '':
                    wikipedia.output(u'No changes needed.')
                    continue
                else:
                    wikipedia.output(diff, colors = colors)
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
