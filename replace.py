# -*- coding: utf-8  -*-
"""
-sql       - Retrieve information from a local dump (http://download.wikimedia.org).
             Argument can also be given as "-sql:filename".
-file      - Retrieve information from a local text file.
             Will read any [[wiki link]] and use these articles
             Argument can also be given as "-file:filename".
-regex     - Make replacements using regular expressions. If this argument isn't
             given, the bot will make simple text replacements.
other:     - First argument is the old text, second argument is the new text.
             if the -regex argument is given, the first argument will be
             regarded as a regular expression, and the second argument might
             contain expressions like \\1 or \g<name>.

NOTE: Use either -sql or -file, but don't use both.

Examples:

If you want to change templates from the old syntax, e.g. {{msg:Stub}}, to the
new syntax, e.g. {{Stub}}, download an SQL dump file from
http://download.wikimedia.org, then use this command:

    python replace.py -sql -regex "{{msg:(.*?)}}" "{{\\1}}"

If you want to fix typos, e.g. Errror -> Error, use this:

    python replace.py -sql "Errror" "Error"
"""
#
# (C) Daniel Herding, 2004
#
# Distributed under the terms of the PSF license.
#

import sys, re
import wikipedia, config

# taken from interwiki.py
def showDiff(oldtext, newtext):
    import difflib
    sep = '\r\n'
    ol = oldtext.split(sep)
    if len(ol) == 1:
        sep = '\n'
        ol = oldtext.split(sep)
    nl = newtext.split(sep)
    for line in difflib.ndiff(ol,nl):
        if line[0] in ['+','-']:
            wikipedia.output(line)

# Generator which will yield pages that might contain text to replace.
# These pages will be retrieved from a local sql dump file.
def read_pages_from_sql_dump(sqlfilename, old, regex):
    import sqldump
    dump = sqldump.SQLdump(sqlfilename, wikipedia.myencoding())
    for entry in dump.entries():
        if regex:
            if old.search(entry.text):
                yield wikipedia.PageLink(wikipedia.mylang, entry.full_title())
        else:
            if entry.text.find(old) != -1:
                yield wikipedia.PageLink(wikipedia.mylang, entry.full_title())

# Generator which will yield pages that might contain text to replace.
# These pages might be retrieved from a text file.
def read_pages_from_text_file(textfilename, old, regex):
        f = open(textfilename, 'r')
        # regular expression which will find [[wiki links]]
        R = re.compile(r'.*\[\[([^\]]*)\]\].*')
        m = False
        for line in f.readlines():
            m=R.match(line)
            if m:
                yield wikipedia.PageLink(wikipedia.mylang, m.group(1))
        f.close()

# Generator which will yield pages that might contain text to replace.
# These pages might be retrieved from a local sql dump file or a text file.
# TODO: Make MediaWiki's search feature available.
def generator(source, old, regex, textfilename = None, sqlfilename = None):
    if source == 'sqldump':
        for pl in read_pages_from_sql_dump(sqlfilename, old, regex):
            yield pl
    elif source == 'textfile':
        for pl in read_pages_from_text_file(textfilename, old, regex):
            yield pl

# How we want to retrieve information on which pages need to be changed.
# Can either be 'sqldump' or 'textfile'.
source = None
# First element is original text, second element is replacement text
replacements = []
# Should the elements elements of 'replacements' be interpreted as regular
# expressions?
regex = False
sqlfilename = ''
textfilename = ''

for arg in sys.argv[1:]:
    arg = unicode(arg, config.console_encoding)
    if wikipedia.argHandler(arg):
        pass
    elif arg == '-regex':
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
    else:
        replacements.append(arg)

if source == None or len(replacements) != 2:
    print 'Please open replace.py with a text editor for syntax information and examples.'
    sys.exit()

old = replacements[0]
new = replacements[1]

if regex:
    old = re.compile(old)

acceptall = False

for pl in generator(source, old, regex, textfilename, sqlfilename):
    # print pl.linkname()
    original_text = pl.get()
    if regex:
        new_text = old.sub(new, original_text)
    else:
        new_text = original_text.replace(old, new)
    if new_text == original_text:
        print 'No changes were necessary in %s' % pl.linkname()
    else:
        showDiff(original_text, new_text)
        if not acceptall:
            choice = wikipedia.input(u'Do you want to accept these changes? [y|n|a(ll)]')
        if choice in ['a', 'A']:
            acceptall = True
            choice = 'y'
        if choice in ['y', 'Y']:
            pl.put(new_text)

