# -*- coding: utf-8  -*-
"""
-sql        - Retrieve information from a local dump (http://download.wikimedia.org).
              Argument can also be given as "-sql:filename".
-file       - Retrieve information from a local text file.
              Will read any [[wiki link]] and use these articles
              Argument can also be given as "-file:filename".
-page       - Only edit a single page.
              Argument can also be given as "-page:pagename".
-regex      - Make replacements using regular expressions. If this argument
              isn't given, the bot will make simple text replacements.
-except:XYZ - Ignore pages which contain XYZ. If the -regex argument is given,
              the XYZ will be regarded as a regular expression.
-fix:XYZ    - Perform one of the predefined replacements tasks, which are given
              in the dictionary 'fixes' below.
              The -regex argument and given replacements will be ignored if
              you use -fix.
other:      - First argument is the old text, second argument is the new text.
              If the -regex argument is given, the first argument will be
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

If you have a page called 'John Doe' and want to convert HTML to wiki tags, use:
    
    python replace.py -page:John_Doe -fix:HTML
"""
#
# (C) Daniel Herding, 2004
#
# Distributed under the terms of the PSF license.
#

import sys, re
import wikipedia, config

# Summary messages
msg = {
       'en':u'Robot: Automated text replacement',
       'de':u'Bot: Automatisierte Textersetzung',
      }

# Predefinded fixes
fixes = {
    # These replacements will convert HTML to wiki syntax where possible, and
    # make remaining tags XHTML compliant.
    'HTML': {
        'regex': True,
        'exceptions':  ['<nowiki>'],
        'msg': {
               'en':u'Robot: Converting/fixing HTML',
               'de':u'Bot: konvertiere/korrigiere HTML',
              },
        'replacements': {
            # everything case-insensitive (?i)
            # keep in mind that MediaWiki automatically converts <br> to <br />
            # when rendering pages, so you might comment the next two lines out
            # to save some time/edits.
            r'(?i)<br>':                      r'<br />',
            # linebreak with attributes
            r'(?i)<br ([^>/]+?)>':            r'<br \1 />',
            r'(?i)<b>(.*?)</b>':              r"'''\1'''",
            r'(?i)<strong>(.*?)</strong>':    r"'''\1'''",
            r'(?i)<i>(.*?)</i>':              r"''\1''",
            r'(?i)<em>(.*?)</em>':            r"''\1''",
            # horizontal line without attributes in a single line
            r'(?i)([\r\n])<hr[ /]*>([\r\n])': r'\1----\2',
            # horizontal line without attributes with more text in the same line
            r'(?i) +<hr[ /]*> +':             r'\r\n----\r\n',
            # horizontal line with attributes; can't be done with wiki syntax
            r'(?i)<hr ([^>/]+?)>':            r'<hr \1 />',
            # a header where only spaces are in the same line
            r'(?i)([\r\n]) *<h1> *([^<]+?) *</h1> *([\r\n])':  r"\1= \2 =\3",
            r'(?i)([\r\n]) *<h2> *([^<]+?) *</h2> *([\r\n])':  r"\1== \2 ==\3",
            r'(?i)([\r\n]) *<h3> *([^<]+?) *</h3> *([\r\n])':  r"\1=== \2 ===\3",
            r'(?i)([\r\n]) *<h4> *([^<]+?) *</h4> *([\r\n])':  r"\1==== \2 ====\3",
            r'(?i)([\r\n]) *<h5> *([^<]+?) *</h5> *([\r\n])':  r"\1===== \2 =====\3",
            r'(?i)([\r\n]) *<h6> *([^<]+?) *</h6> *([\r\n])':  r"\1====== \2 ======\3",
        }
    }
}

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
def read_pages_from_sql_dump(sqlfilename, replacements, exceptions, regex):
    import sqldump
    dump = sqldump.SQLdump(sqlfilename, wikipedia.myencoding())
    for entry in dump.entries():
        skip_page = False
        for exception in exceptions:
            if regex:
                exception = re.compile(exception)
                if exception.search(entry.text):
                    skip_page = True
                    break
            else:
                if entry.text.find(exception) != -1:
                    skip_page = True
                    break
        if not skip_page:
            for old in replacements.keys():
                if regex:
                    old = re.compile(old)
                    if old.search(entry.text):
                        yield wikipedia.PageLink(wikipedia.mylang, entry.full_title())
                        break
                else:
                    if entry.text.find(old) != -1:
                        yield wikipedia.PageLink(wikipedia.mylang, entry.full_title())
                        break

# Generator which will yield pages that might contain text to replace.
# These pages might be retrieved from a text file.
def read_pages_from_text_file(textfilename):
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
def generator(source, replacements, exceptions, regex, textfilename = None, sqlfilename = None, pagename = None):
    if source == 'sqldump':
        for pl in read_pages_from_sql_dump(sqlfilename, replacements, exceptions, regex):
            yield pl
    elif source == 'textfile':
        for pl in read_pages_from_text_file(textfilename):
            yield pl
    elif source == 'singlepage':
        yield wikipedia.PageLink(wikipedia.mylang, pagename)

# How we want to retrieve information on which pages need to be changed.
# Can either be 'sqldump' or 'textfile'.
source = None
# Array which will collect commandline parameters.
# First element is original text, second element is replacement text.
commandline_replacements = []
# Dictionary where keys are original texts and values are replacement texts.
replacements = {}
# Don't edit pages which contain certain texts
exceptions = []
# Should the elements elements of 'replacements' and 'exceptions' be interpreted
# as regular expressions?
regex = False
# Predefined fixes from above dictionary
fix = None
sqlfilename = ''
textfilename = ''
pagename = ''

# Summary message
wikipedia.setAction(msg[wikipedia.chooselang(wikipedia.mylang, msg)])

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
    elif arg.startswith('-page'):
        if len(arg) == 5:
            pagename = wikipedia.input(u'Which page do you want to chage?')
        else:
            pagename = arg[6:]
        source = 'singlepage'
    elif arg.startswith('-except:'):
        exceptions.append(arg[8:])
    elif arg.startswith('-fix:'):
        fix = arg[5:]
    else:
        commandline_replacements.append(arg)

if source == None:
    print 'Please open replace.py with a text editor for syntax information and examples.'
    sys.exit()
if (len(commandline_replacements) == 2 and fix == None):
    replacements[commandline_replacements[0]] = commandline_replacements[1]
elif fix == None:
    old = wikipedia.input(u'Please enter the text that should be replaced:')
    new = wikipedia.input(u'Please enter the new text:')
    replacements[old] = new
    while True:
        old = wikipedia.input(u'Please enter another text that should be replaced, or press Enter to start:')
        if old == '':
            break
        new = wikipedia.input(u'Please enter the new text:')
        replacements[old] = new

else:
    # Perform one of the predefined actions
    fix = fixes[fix]
    if fix.has_key('regex'):
        regex = fix['regex']
    if fix.has_key('msg'):
        wikipedia.setAction(fix['msg'][wikipedia.chooselang(wikipedia.mylang, fix['msg'])])
    if fix.has_key('exceptions'):
        exceptions = fix['exceptions']
    replacements = fix['replacements']

acceptall = False

for pl in generator(source, replacements, exceptions, regex, textfilename, sqlfilename, pagename):
    # print pl.linkname()
    try:
        original_text = pl.get()
    except wikipedia.NoPage:
        wikipedia.output('Page %s not found' % pl.linkname())
        continue
    except wikipedia.LockedPage:
        wikipedia.output('Skipping locked page %s' % pl.linkname())
        continue
    
    skip_page = False
    for exception in exceptions:
        if regex:
            exception = re.compile(exception)
            hit = exception.search(original_text)
            if hit:
                wikipedia.output('Skipping %s because it contains %s' % (pl.linkname(), hit.group(0)))
                # Does anyone know how to break out of the _outer_ loop?
                # Then we wouldn't need the skip_page variable.
                skip_page = True
                break
        else:
            hit = original_text.find(exception)
            if hit != -1:
                wikipedia.output('Skipping %s because it contains %s' % (pl.linkname(), original_text[hit:hit + len(exception)]))
                skip_page = True
                break
    if not skip_page:
        # create a copy of the original text to work on, so we can later compare
        # if any changes were made
        new_text = original_text
        for old, new in replacements.items():
            if regex:
                # TODO: compiling the regex each time might be inefficient
                old = re.compile(old)
                new_text = old.sub(new, new_text)
            else:
                new_text = new_text.replace(old, new)
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
