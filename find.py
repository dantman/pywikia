# -*- coding: utf-8  -*-
"""
Base replace.py, this bot will make find in SQL dump.
Download please "cur table", see http://download.wikimedia.org).

Use: python find.py
Use: Text that should be searched (Enter exits):

"""
#
# (C) e2m, 2004
#
# Distributed under the terms of the PSF license.
#
# Modified by [[wikipedia:pt:Wikipedia:Coordenação robótica]]
#

__version__ = '$Id$'

from __future__ import generators
import sys, re
import wikipedia, config

def read_pages_from_sql_dump(sqlfilename, title):
    import sqldump
    dump = sqldump.SQLdump(sqlfilename, wikipedia.myencoding())
    for entry in dump.entries():
	if title:
	    text=entry.title
	else:
	    text=entry.text
	skip_page = False
        if namespace != -1 and namespace != entry.namespace:
            continue
        if not skip_page:
            for old in replacements.keys():
                if regex:
                    old = re.compile(old)
                    if old.search(text):
                        yield wikipedia.PageLink(wikipedia.getSite(), entry.full_title())
                        break
                else:
                    if text.find(old) != -1:
                       yield wikipedia.PageLink(wikipedia.getSite(), entry.full_title())
                       break

def generator(source, replacements, exceptions, regex, namespace, title, textfilename = None, sqlfilename = None, pagenames = None):
    source == 'sqldump'
    for pl in read_pages_from_sql_dump(sqlfilename, title):
        yield pl

source = None
replacements = {}
exceptions = []
regex = False
title = False
count = None
sqlfilename = 'dump.sql'
textfilename = ''
pagenames = []
namespace = -1

# expand -sql: -page: -file:
for arg in sys.argv[1:]:
    arg == ('')
    source = 'sqldump'

if count == None:
    old = wikipedia.input(u'Text that should be searched (Enter exits):')
    new = " "
    change = ' (-' + old + ' +' + new
    replacements[old] = new
    while True:
        old = wikipedia.input(u'Text that should be searched (Enter exits):')
        if old == '':
            change = change + ')'
            break
        new = " "
        change = change + ' & -' + old + ' +' + new
        replacements[old] = new

# Save search in find.dat
count = 0
import codecs
arq = codecs.open('find.dat', 'w', 'utf-8')
for pl in generator(source, replacements, exceptions, regex, namespace, title, textfilename, sqlfilename, pagenames):
    arq.write("# [[%s]] \n" % pl.linkname())
    count +=1
    print str(count), pl.linkname()
arq.close()
