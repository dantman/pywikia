# -*- coding: utf-8  -*-
'''
This bot will find in SQL dump or in Wikipedia sites.
Download please "cur table", see http://download.wikimedia.org).

You can run the bot with the following commandline parameters:

-sql         - Search information from a local SQL dump.
               Argument can also be given as "-sql:filename".
-file        - Search information from a local text file.
               Argument can also be given as "-file:filename".
-page        - Only search a single page.
               Argument can also be given as "-page:pagename".

Use: python find.py -argument

'''
#
# (C) E2m, 2004
# (C) Leonardo Gregianin, 2004-2005
#
# Distributed under the terms of the PSF license.
#

from __future__ import generators
import sys, re, codecs
import wikipedia, config, sqldump

def read_pages_from_sql_dump(sqlfilename, title):
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

#TODO: all
def read_pages_from_text_file(textfilename):
    pageR = re.compile("\((\d+),"      # cur_id             (page ID number)
                     + "(\d+),"        # cur_namespace      (namespace number)
                     + "'(.*?)',"      # cur_title          (page title w/o namespace)
                     + "'(.*?)',"      # cur_text           (page contents)
                     + "'(.*?)',"      # cur_comment        (last edit's summary text)
                     + "(\d+),"        # cur_user           (user ID of last contributor)
                     + "'(.*?)',"      # cur_user_text      (user name)
                     + "'(\d{14})',"   # cur_timestamp      (time of last edit)
                     + "'(.*?)',"      # cur_restrictions   (protected pages have 'sysop' here)
                     + "(\d+),"        # cur_counter        (view counter, disabled on WP)
                     + "([01]),"       # cur_is_redirect
                     + "([01]),"       # cur_minor_edit
                     + "([01]),"       # cur_is_new
                     + "([\d\.]+?),"   # cur_random         (for random page function)
                     + "'(\d{14})',"   # inverse_timestamp  (obsolete)
                     + "'(\d{14})'\)") # cur_touched        (cache update timestamp)
    print 'Reading file'
    arq = codecs.open(textfilename, 'r', 'utf-8')
#    for pl in generator(source, replacements, exceptions, namespace, regex, title, textfilename, sqlfilename, pagenames):
    eof = False
    while not eof:
        line = arq.readline()
        if line == '':
            print 'End of file.'
        eof = True
        entries = []
        for id, namespace, title, text, comment, userid, username, timestamp, restrictions, counter, redirect, minor, new, random, inversetimestamp, touched in pageR.findall(line):
             new_entry = SQLentry(id, namespace, title, text, comment, userid, username, timestamp, restrictions, counter, redirect, minor, new, random, inversetimestamp, touched)
             yield new_entry
    print 'End of file.'
    arq.close()

#TODO: all
def read_pages_from_wiki_page(pagetitle):
    '''
    Generator which will yield pages that are listed in a wiki page. Will
    regard everything inside [[double brackets]] as a page name, except for
    interwiki and category links, and yield PageLinks for these pages.
    '''

    listpage = wikipedia.PageLink(wikipedia.getSite(), pagetitle)
    list = wikipedia.get(listpage, read_only = True)

def generator(source, replacements, exceptions, regex, namespace, title, textfilename = None, sqlfilename = None, pagenames = None):
    #-sql
    if source == 'sqldump':
        for pl in read_pages_from_sql_dump(sqlfilename, title):
            yield pl
    #-file
    elif source == 'textfile':
        for pl in read_pages_from_text_file(textfilename):
            yield pl
    #-page
    elif source == 'userinput':
        for pagename in pagenames:
            yield wikipedia.PageLink(wikipedia.getSite(), pagename)

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

try:
    for arg in sys.argv[1:]:
        arg = wikipedia.argHandler(arg)
        if arg:
            if arg == '-regex':
                regex = True
            elif arg.startswith('-file'):
                if len(arg) == 5:
                    textfilename = wikipedia.input(u'Please enter the filename:')
                else:
                    textfilename = arg[6:]
                source = 'textfile'
            elif arg.startswith('-sql'):
                if len(arg) == 4:
                    sqlfilename = wikipedia.input(u'Please enter the SQL dump\'s filename:')
                else:
                    sqlfilename = arg[5:]
                source = 'sqldump'
                wikipedia.stopme()
            elif arg.startswith('-page'):
                if len(arg) == 5:
                    pagenames.append(wikipedia.input(u'Which page do you want to find?'))
                else:
                    pagenames.append(arg[6:])
                source = 'userinput'
            else:
                commandline_replacements.append(arg)
            
    #TODO: def search
    if count == None:
        old = wikipedia.input(u'Text search (Warning! Case and Acent Sensitive):')
        new = " "
        replacements[old] = new

    # TODO: def record
    # Save search in find.dat
    count = 0
    arq = codecs.open('find.dat', 'w', 'utf-8')
    for pl in generator(source, replacements, exceptions, regex, namespace, title, textfilename, sqlfilename, pagenames):
        arq.write("# [[%s]] \n" % pl.linkname())
        count +=1
        print str(count), pl.linkname()
    arq.close()
except:
    wikipedia.stopme()
    raise
else:
    wikipedia.stopme()

