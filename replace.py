# -*- coding: utf-8  -*-
"""
This bot will make direct text replacements. It will retrieve information on
which pages might need changes either from an SQL dump or a text file, or only
change a single page.

You can run the bot with the following commandline parameters:

-sql        - Retrieve information from a local SQL dump (cur table, see
              http://download.wikimedia.org).
              Argument can also be given as "-sql:filename".
-file       - Retrieve information from a local text file.
              Will read any [[wiki link]] and use these articles.
              Argument can also be given as "-file:filename".
-page       - Only edit a single page.
              Argument can also be given as "-page:pagename". You can give this
              parameter multiple times to edit multiple pages.
-regex      - Make replacements using regular expressions. If this argument
              isn't given, the bot will make simple text replacements.
-except:XYZ - Ignore pages which contain XYZ. If the -regex argument is given,
              XYZ will be regarded as a regular expression.
-fix:XYZ    - Perform one of the predefined replacements tasks, which are given
              in the dictionary 'fixes' defined inside this file.
              The -regex argument and given replacements will be ignored if
              you use -fix.
              Currently available predefined fixes are:
                  * HTML - convert HTML tags to wiki syntax, and fix XHTML
-always     - Don't prompt you for each replacement
other:      - First argument is the old text, second argument is the new text.
              If the -regex argument is given, the first argument will be
              regarded as a regular expression, and the second argument might
              contain expressions like \\1 or \g<name>.

NOTE: Only use either -sql or -file or -page, but don't mix them.

Examples:

If you want to change templates from the old syntax, e.g. {{msg:Stub}}, to the
new syntax, e.g. {{Stub}}, download an SQL dump file (cur table) from
http://download.wikimedia.org, then use this command:

    python replace.py -sql -regex "{{msg:(.*?)}}" "{{\\1}}"

If you have a dump called foobar.sql and want to fix typos, e.g.
Errror -> Error, use this:

    python replace.py -sql:foobar.sql "Errror" "Error"

If you have a page called 'John Doe' and want to convert HTML tags to wiki
syntax, use:
    
    python replace.py -page:John_Doe -fix:HTML
"""
#
# (C) Daniel Herding, 2004
#
# Distributed under the terms of the PSF license.
#

import sys, re
import wikipedia, config

# Summary messages in different languages
# NOTE: Predefined replacement tasks might use their own dictionary, see 'fixes'
# below.
msg = {
       'de':u'Bot: Automatisierte Textersetzung',
       'en':u'Robot: Automated text replacement',
       'es':u'Robot: Reemplazo automático de texto',
       }

# Predefined replacements tasks.
fixes = {
    # temporarily needed for moving de: autobahns
    'BAB': {
        'regex': False,
        'replacements': {
            '[[A100 (Autobahn)|A&nbsp;100]]': '[[A 100]]',
            '[[A103 (Autobahn)|A&nbsp;103]]': '[[A 103]]',
            '[[A104 (Autobahn)|A&nbsp;104]]': '[[A 104]]',
            '[[A111 (Autobahn)|A&nbsp;111]]': '[[A 111]]',
            '[[A113 (Autobahn)|A&nbsp;113]]': '[[A 113]]',
            '[[A114 (Autobahn)|A&nbsp;114]]': '[[A 114]]',
            '[[A115 (Autobahn)|A&nbsp;115]]': '[[A 115]]',
            '[[A143 (Autobahn)|A&nbsp;143]]': '[[A 143]]',
            '[[A210 (Autobahn)|A&nbsp;210]]': '[[A 210]]',
            '[[A215 (Autobahn)|A&nbsp;215]]': '[[A 215]]',
            '[[A226 (Autobahn)|A&nbsp;226]]': '[[A 226]]',
            '[[A241 (Autobahn)|A&nbsp;241]]': '[[A 241]]',
            '[[A250 (Autobahn)|A&nbsp;250]]': '[[A 250]]',
            '[[A252 (Autobahn)|A&nbsp;252]]': '[[A 252]]',
            '[[A253 (Autobahn)|A&nbsp;253]]': '[[A 253]]',
            '[[A255 (Autobahn)|A&nbsp;255]]': '[[A 255]]',
            '[[A261 (Autobahn)|A&nbsp;261]]': '[[A 261]]',
            '[[A270 (Autobahn)|A&nbsp;270]]': '[[A 270]]',
            '[[A280 (Autobahn)|A&nbsp;280]]': '[[A 280]]',
            '[[A281 (Autobahn)|A&nbsp;281]]': '[[A 281]]',
            '[[A293 (Autobahn)|A&nbsp;293]]': '[[A 293]]',
            '[[A352 (Autobahn)|A&nbsp;352]]': '[[A 352]]',
            '[[A388 (Autobahn)|A&nbsp;388]]': '[[A 388]]',
            '[[A391 (Autobahn)|A&nbsp;391]]': '[[A 391]]',
            '[[A392 (Autobahn)|A&nbsp;392]]': '[[A 392]]',
            '[[A395 (Autobahn)|A&nbsp;395]]': '[[A 395]]',
            '[[A443 (Autobahn)|A&nbsp;443]]': '[[A 443]]',
            '[[A445 (Autobahn)|A&nbsp;445]]': '[[A 445]]',
            '[[A480 (Autobahn)|A&nbsp;480]]': '[[A 480]]',
            '[[A485 (Autobahn)|A&nbsp;485]]': '[[A 485]]',
            '[[A516 (Autobahn)|A&nbsp;516]]': '[[A 516]]',
            '[[A524 (Autobahn)|A&nbsp;524]]': '[[A 524]]',
            '[[A535 (Autobahn)|A&nbsp;535]]': '[[A 535]]',
            '[[A540 (Autobahn)|A&nbsp;540]]': '[[A 540]]',
            '[[A542 (Autobahn)|A&nbsp;542]]': '[[A 542]]',
            '[[A544 (Autobahn)|A&nbsp;544]]': '[[A 544]]',
            '[[A553 (Autobahn)|A&nbsp;553]]': '[[A 553]]',
            '[[A555 (Autobahn)|A&nbsp;555]]': '[[A 555]]',
            '[[A559 (Autobahn)|A&nbsp;559]]': '[[A 559]]',
            '[[A560 (Autobahn)|A&nbsp;560]]': '[[A 560]]',
            '[[A562 (Autobahn)|A&nbsp;562]]': '[[A 562]]',
            '[[A565 (Autobahn)|A&nbsp;565]]': '[[A 565]]',
            '[[A571 (Autobahn)|A&nbsp;571]]': '[[A 571]]',
            '[[A573 (Autobahn)|A&nbsp;573]]': '[[A 573]]',
            '[[A602 (Autobahn)|A&nbsp;602]]': '[[A 602]]',
            '[[A620 (Autobahn)|A&nbsp;620]]': '[[A 620]]',
            '[[A623 (Autobahn)|A&nbsp;623]]': '[[A 623]]',
            '[[A643 (Autobahn)|A&nbsp;643]]': '[[A 643]]',
            '[[A648 (Autobahn)|A&nbsp;648]]': '[[A 648]]',
            '[[A650 (Autobahn)|A&nbsp;650]]': '[[A 650]]',
            '[[A652 (Autobahn)|A&nbsp;652]]': '[[A 652]]',
            '[[A656 (Autobahn)|A&nbsp;656]]': '[[A 656]]',
            '[[A659 (Autobahn)|A&nbsp;659]]': '[[A 659]]',
            '[[A661 (Autobahn)|A&nbsp;661]]': '[[A 661]]',
            '[[A671 (Autobahn)|A&nbsp;671]]': '[[A 671]]',
            '[[A672 (Autobahn)|A&nbsp;672]]': '[[A 672]]',
            '[[A831 (Autobahn)|A&nbsp;831]]': '[[A 831]]',
            '[[A861 (Autobahn)|A&nbsp;861]]': '[[A 861]]',
            '[[A862 (Autobahn)|A&nbsp;862]]': '[[A 862]]',
            '[[A864 (Autobahn)|A&nbsp;864]]': '[[A 864]]',
            '[[A952 (Autobahn)|A&nbsp;952]]': '[[A 952]]',
            '[[A980 (Autobahn)|A&nbsp;980]]': '[[A 980]]',
            '[[A995 (Autobahn)|A&nbsp;995]]': '[[A 995]]',
            '[[A26 (Autobahn)|A&nbsp;26]]': '[[A 26]]',
            '[[A27 (Autobahn)|A&nbsp;27]]': '[[A 27]]',
            '[[A28 (Autobahn)|A&nbsp;28]]': '[[A 28]]',
            '[[A29 (Autobahn)|A&nbsp;29]]': '[[A 29]]',
            '[[A30 (Autobahn)|A&nbsp;30]]': '[[A 30]]',
            '[[A31 (Autobahn)|A&nbsp;31]]': '[[A 31]]',
            '[[A33 (Autobahn)|A&nbsp;33]]': '[[A 33]]',
            '[[A37 (Autobahn)|A&nbsp;37]]': '[[A 37]]',
            '[[A38 (Autobahn)|A&nbsp;38]]': '[[A 38]]',
            '[[A39 (Autobahn)|A&nbsp;39]]': '[[A 39]]',
            '[[A40 (Autobahn)|A&nbsp;40]]': '[[A 40]]',
            '[[A42 (Autobahn)|A&nbsp;42]]': '[[A 42]]',
            '[[A43 (Autobahn)|A&nbsp;43]]': '[[A 43]]',
            '[[A44 (Autobahn)|A&nbsp;44]]': '[[A 44]]',
            '[[A45 (Autobahn)|A&nbsp;45]]': '[[A 45]]',
            '[[A46 (Autobahn)|A&nbsp;46]]': '[[A 46]]',
            '[[A48 (Autobahn)|A&nbsp;48]]': '[[A 48]]',
            '[[A49 (Autobahn)|A&nbsp;49]]': '[[A 49]]',
            '[[A57 (Autobahn)|A&nbsp;57]]': '[[A 57]]',
            '[[A59 (Autobahn)|A&nbsp;59]]': '[[A 59]]',
            '[[A60 (Autobahn)|A&nbsp;60]]': '[[A 60]]',
            '[[A61 (Autobahn)|A&nbsp;61]]': '[[A 61]]',
            '[[A62 (Autobahn)|A&nbsp;62]]': '[[A 62]]',
            '[[A63 (Autobahn)|A&nbsp;63]]': '[[A 63]]',
            '[[A64 (Autobahn)|A&nbsp;64]]': '[[A 64]]',
            '[[A65 (Autobahn)|A&nbsp;65]]': '[[A 65]]',
            '[[A66 (Autobahn)|A&nbsp;66]]': '[[A 66]]',
            '[[A67 (Autobahn)|A&nbsp;67]]': '[[A 67]]',
            '[[A70 (Autobahn)|A&nbsp;70]]': '[[A 70]]',
            '[[A71 (Autobahn)|A&nbsp;71]]': '[[A 71]]',
            '[[A72 (Autobahn)|A&nbsp;72]]': '[[A 72]]',
            '[[A73 (Autobahn)|A&nbsp;73]]': '[[A 73]]',
            '[[A81 (Autobahn)|A&nbsp;81]]': '[[A 81]]',
            '[[A92 (Autobahn)|A&nbsp;92]]': '[[A 92]]',
            '[[A93 (Autobahn)|A&nbsp;93]]': '[[A 93]]',
            '[[A94 (Autobahn)|A&nbsp;94]]': '[[A 94]]',
            '[[A95 (Autobahn)|A&nbsp;95]]': '[[A 95]]',
            '[[A96 (Autobahn)|A&nbsp;96]]': '[[A 96]]',
            '[[A98 (Autobahn)|A&nbsp;98]]': '[[A 98]]',
            '[[A99 (Autobahn)|A&nbsp;99]]': '[[A 99]]',
            '[[A99 (Autobahn)|A&nbsp;99]]': '[[A 99]]',
            }
        },
    # These replacements will convert HTML to wiki syntax where possible, and
    # make remaining tags XHTML compliant.
    'HTML': {
        'regex': True,
        # We don't want to mess up pages which discuss HTML tags, so we skip
        # all pages which contain nowiki tags.
        'exceptions':  ['<nowiki>'],
        'msg': {
               'en':u'Robot: converting/fixing HTML',
               'de':u'Bot: konvertiere/korrigiere HTML',
              },
        'replacements': {
            # Everything case-insensitive (?i)
            # Keep in mind that MediaWiki automatically converts <br> to <br />
            # when rendering pages, so you might comment the next two lines out
            # to save some time/edits.
            #r'(?i)<br>':                      r'<br />',
            # linebreak with attributes
            #r'(?i)<br ([^>/]+?)>':            r'<br \1 />',
            r'(?i)<b>(.*?)</b>':              r"'''\1'''",
            r'(?i)<strong>(.*?)</strong>':    r"'''\1'''",
            r'(?i)<i>(.*?)</i>':              r"''\1''",
            r'(?i)<em>(.*?)</em>':            r"''\1''",
            # horizontal line without attributes in a single line
            r'(?i)([\r\n])<hr[ /]*>([\r\n])': r'\1----\2',
            # horizontal line without attributes with more text in the same line
            r'(?i) +<hr[ /]*> +':             r'\r\n----\r\n',
            # horizontal line with attributes; can't be done with wiki syntax
            # so we only make it XHTML compliant
            r'(?i)<hr ([^>/]+?)>':            r'<hr \1 />',
            # a header where only spaces are in the same line
            r'(?i)([\r\n]) *<h1> *([^<]+?) *</h1> *([\r\n])':  r"\1= \2 =\3",
            r'(?i)([\r\n]) *<h2> *([^<]+?) *</h2> *([\r\n])':  r"\1== \2 ==\3",
            r'(?i)([\r\n]) *<h3> *([^<]+?) *</h3> *([\r\n])':  r"\1=== \2 ===\3",
            r'(?i)([\r\n]) *<h4> *([^<]+?) *</h4> *([\r\n])':  r"\1==== \2 ====\3",
            r'(?i)([\r\n]) *<h5> *([^<]+?) *</h5> *([\r\n])':  r"\1===== \2 =====\3",
            r'(?i)([\r\n]) *<h6> *([^<]+?) *</h6> *([\r\n])':  r"\1====== \2 ======\3",
            # TODO: maybe we can make the bot replace <p> tags with \r\n's.
        }
    }
}

# Taken from interwiki.py. TODO: move to wikipedia.py.
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

def read_pages_from_sql_dump(sqlfilename, replacements, exceptions, regex):
    '''
    Generator which will yield PageLinks to pages that might contain text to
    replace. These pages will be retrieved from a local sql dump file
    (cur table).

    Arguments:
        * sqlfilename  - the dump's path, either absolute or relative
        * replacements - a dictionary where old texts are keys and new texts
                         are values
        * exceptions   - a list of strings; pages which contain one of these
                         won't be changed.
        * regex        - if the entries of replacements and exceptions should
                         be interpreted as regular expressions
    '''
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

def read_pages_from_text_file(textfilename):
    '''
    Generator which will yield pages that are listed in a text file created by
    the bot operator. Will regard everything inside [[double brackets]] as a
    page name, and yield PageLinks for these pages.

    Arguments:
        * textfilename - the textfile's path, either absolute or relative
    '''
    f = open(textfilename, 'r')
    # regular expression which will find [[wiki links]]
    R = re.compile(r'.*\[\[([^\]]*)\]\].*')
    m = False
    for line in f.readlines():
        # BUG: this will only find one link per line.
        # TODO: use findall() instead.
        m=R.match(line)
        if m:
            yield wikipedia.PageLink(wikipedia.mylang, m.group(1))
    f.close()

# TODO: Make MediaWiki's search feature available.
def generator(source, replacements, exceptions, regex, textfilename = None, sqlfilename = None, pagenames = None):
    '''
    Generator which will yield PageLinks for pages that might contain text to
    replace. These pages might be retrieved from a local SQL dump file or a
    text file, or as a list of pages entered by the user.

    Arguments:
        * source       - where the bot should retrieve the page list from.
                         can be 'sqldump', 'textfile' or 'userinput'.
        * replacements - a dictionary where keys are original texts and values
                         are replacement texts.
        * exceptions   - a list of strings; pages which contain one of these
                         won't be changed.
        * regex        - if the entries of replacements and exceptions should
                         be interpreted as regular expressions
        * textfilename - the textfile's path, either absolute or relative, which
                         will be used when source is 'textfile'.
        * sqlfilename  - the dump's path, either absolute or relative, which
                         will be used when source is 'sqldump'.
        * pagenames    - a list of pages which will be used when source is
                         'userinput'.
    '''
    if source == 'sqldump':
        for pl in read_pages_from_sql_dump(sqlfilename, replacements, exceptions, regex):
            yield pl
    elif source == 'textfile':
        for pl in read_pages_from_text_file(textfilename):
            yield pl
    elif source == 'userinput':
        for pagename in pagenames:
            yield wikipedia.PageLink(wikipedia.mylang, pagename)

# How we want to retrieve information on which pages need to be changed.
# Can either be 'sqldump', 'textfile' or 'userinput'.
source = None
# Array which will collect commandline parameters.
# First element is original text, second element is replacement text.
commandline_replacements = []
# A dictionary where keys are original texts and values are replacement texts.
replacements = {}
# Don't edit pages which contain certain texts.
exceptions = []
# Should the elements of 'replacements' and 'exceptions' be interpreted
# as regular expressions?
regex = False
# Predefined fixes from dictionary 'fixes' (see above).
fix = None
# the dump's path, either absolute or relative, which will be used when source
# is 'sqldump'.
sqlfilename = ''
# the textfile's path, either absolute or relative, which will be used when
# source is 'textfile'.
textfilename = ''
# a list of pages which will be used when source is 'userinput'.
pagenames = []
# will become True when the user presses a ('yes to all') or uses the -always
# commandline paramater.
acceptall = False

# Load default summary message.
wikipedia.setAction(wikipedia.translate(wikipedia.mylang, msg))

# Read commandline parameters.
for arg in sys.argv[1:]:
    # Convert argument from the encoding the user's shell uses to Unicode
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
            pagenames.append(wikipedia.input(u'Which page do you want to chage?'))
        else:
            pagenames.append(arg[6:])
        source = 'userinput'
    elif arg.startswith('-except:'):
        exceptions.append(arg[8:])
    elif arg.startswith('-fix:'):
        fix = arg[5:]
    elif arg == '-always':
        acceptall = True
    else:
        commandline_replacements.append(arg)

if source == None or len(commandline_replacements) not in [0, 2]:
    # syntax error, show help text from the top of this file
    wikipedia.output(__doc__, 'utf-8')
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
    # Perform one of the predefined actions.
    fix = fixes[fix]
    if fix.has_key('regex'):
        regex = fix['regex']
    if fix.has_key('msg'):
        wikipedia.setAction(wikipedia.translate(wikipedia.mylang, fix['msg']))
    if fix.has_key('exceptions'):
        exceptions = fix['exceptions']
    replacements = fix['replacements']

# Run the generator which will yield PageLinks to pages which might need to be
# changed.
for pl in generator(source, replacements, exceptions, regex, textfilename, sqlfilename, pagenames):
    print ''
    try:
        # Load the page's text from the wiki
        original_text = pl.get()
    except wikipedia.NoPage:
        wikipedia.output(u'Page %s not found' % pl.linkname())
        continue
    except wikipedia.LockedPage:
        wikipedia.output(u'Skipping locked page %s' % pl.linkname())
        continue
    except wikipedia.IsRedirectPage:
        continue
    
    skip_page = False
    # skip all pages that contain certain texts
    for exception in exceptions:
        if regex:
            exception = re.compile(exception)
            hit = exception.search(original_text)
            if hit:
                wikipedia.output(u'Skipping %s because it contains %s' % (pl.linkname(), hit.group(0)))
                # Does anyone know how to break out of the _outer_ loop?
                # Then we wouldn't need the skip_page variable.
                skip_page = True
                break
        else:
            hit = original_text.find(exception)
            if hit != -1:
                wikipedia.output(u'Skipping %s because it contains %s' % (pl.linkname(), original_text[hit:hit + len(exception)]))
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
