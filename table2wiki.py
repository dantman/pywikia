#!/usr/bin/python
# -*- coding: iso-8859-1  -*-
"""
Nifty script to convert HTML-tables to Wikipedia's syntax.


-file:filename
      will read any [[wikipedia link]] and use these articles

-sql:XYZ
      reads a local SQL cur dump, available at http://download.wikimedia.org/.
      Searches for pages with HTML tables, and tries to convert them on the live
      wiki. Example:
      python table2wiki.py -sql:20040711_cur_table.sql.sql -lang:de

SQL-Query

SELECT CONCAT('[[', cur_title, ']]')
       FROM cur
       WHERE (cur_text LIKE '%<table%'
         OR cur_text LIKE '%<TABLE%')
         AND cur_title REGEXP "^[A-N]"
         AND cur_namespace=0
       ORDER BY cur_title
       LIMIT 500


FEATURES
Save against missing </td>
Corrects attributes of tags

KNOW BUGS
Broken HTML-tables will most likely result in broken wiki-tables!
Please check every article you change.


"""

# (C) 2003 Thomas R. Koll, <tomk32@tomk32.de>
#
# Distribute under the terms of the PSF license.
__version__='$Id$'

import re,sys,wikipedia,config,time

myComment = {'de':'Bot: Tabellensyntax konvertiert',
             'en':'User-controlled Bot: table syntax updated',
             'nl':'Tabel gewijzigd van HTML- naar Wikisyntax'
             }
fixedSites = ''
notFixedSites = ''
notFoundSites = ''
quietMode = False # use -quiet to get less output

# if the -file argument is used, page titles are dumped in this array.
# otherwise it will only contain one page.
articles = []    
# if -file is not used, this temporary array is used to read the page title.
page_title = []

action = None
for arg in sys.argv[1:]:
    if arg.startswith('-file:'):

        f=open(arg[6:], 'r')
        R=re.compile(r'.*\[\[([^\]]*)\]\].*')
        m = False
        for line in f.readlines():
            m=R.match(line)            
            if m:
                articles.append(m.group(1))
            else:
                print "ERROR: Did not understand %s line:\n%s" % (
                    arg[6:], repr(line))
        f.close()
    elif arg.startswith('-sql'):
        if len(arg) == 4:
            sqlfilename = wikipedia.input('Please enter the SQL dump\'s filename: ')
        else:
            sqlfilename = arg[5:]
        action = 'parse_sqldump'
    elif arg.startswith('-skip:'):
        articles = articles[articles.index(arg[6:]):]
    elif wikipedia.argHandler(arg):
        pass
    elif arg.startswith('-auto'):
        config.table2wikiAskOnlyWarnings = True
        config.table2wikiSkipWarnings = True
        print "Automatic mode!\n"
    elif arg.startswith('-quiet'):
        quietMode = True
    elif arg.startswith('-debug'):
        articles = "test"
        config.DEBUG = True
    else:
        page_title.append(arg)

# if the page is given as a command line argument,
# connect the title's parts with spaces
if page_title != []:
     page_title = ' '.join(page_title)
     articles.append(page_title)
        
if action == 'parse_sqldump':
    import sqldump
    sqldump = sqldump.SQLdump(sqlfilename, wikipedia.myencoding())
    for page in sqldump.pages():
        if page.text.find('<table') != -1:
            articles.append(page.title)
        
for article in articles:
    if config.DEBUG:
        f = open("table2wiki.testTable")
        text = f.read()
    else:
        pl = wikipedia.PageLink(wikipedia.mylang, article)
        try:
            text = pl.get()
        except wikipedia.NoPage:
            print "ERROR: couldn't find " + article
            notFoundSites = notFoundSites + " " + article
            continue
        except:
            print "Couldn't connect, sleeping for one minute"
            time.sleep(60)
            continue
    warnings = 0
    newText = text
    ##################
    # bring every <tag> into one single line.
    num = 1
    while num != 0:
        newText, num = re.subn("([^\r\n]{1})(<[tT]{1}[dDhHrR]{1})",
                               "\\1\r\n\\2", newText, 0)
        
    ##################
    # every open-tag gets a new line.


    ##################
    # <table> tag with parameters, with more text on the same line
    newText = re.sub("[\r\n]*?<(?i)(table) ([\w\W]*?)>([\w\W]*?)[\r\n ]*",
                     "\r\n{| \\2\r\n\\3", newText, 0)
    # <table> tag without parameters, with more text on the same line
    newText = re.sub("[\r\n]*?<(TABLE|table)>([\w\W]*?)[\r\n ]*",
                     "\r\n{|\n\\2\r\n", newText, 0)
    # <table> tag with parameters, without more text on the same line
    newText = re.sub("[\r\n]*?<(TABLE|table) ([\w\W]*?)>[\r\n ]*",
                     "\r\n{| \\2\r\n", newText, 0)
    # <table> tag without parameters, without more text on the same line
    newText = re.sub("[\r\n]*?<(TABLE|table)>[\r\n ]*",
                     "\r\n{|\r\n", newText, 0)
    # end </table>
    newText = re.sub("[\s]*<\/(TABLE|table)>", "\r\n|}", newText, 0)
    
    ##################
    # captions
    newText = re.sub("<caption ([\w\W]*?)>([\w\W]*?)<\/caption>",
                         "\r\n|+\\1 | \\2", newText, 0)
    newText = re.sub("<caption>([\w\W]*?)<\/caption>",
                     "\r\n|+ \\1", newText, 0)
    
    ##################
    # <th> often people don't write them within <tr>, be warned!
    newText = re.sub("[\r\n]+<(TH|th)([^>]*?)>([\w\W]*?)<\/(th|TH)>",
                     "\r\n!\\2 | \\3\r\n", newText, 0)

    # fail save. sometimes people forget </th>
    newText, n = re.subn("[\r\n]+<(th|TH)>([\w\W]*?)[\r\n]+",
                         "\r\n! \\2\r\n", newText, 0)
    warnings = warnings + n
    newText, n = re.subn("[\r\n]+<(th|TH)([^>]*?)>([\w\W]*?)[\r\n]+",
                             "\r\n!\\2 | \\3\r\n", newText, 0)
    warnings = warnings + n


    ##################
    # very simple <tr>
    newText = re.sub("[\r\n]*<(tr|TR)([^>]*?)>[\r\n]*", "\r\n|-----\\2\r\n", newText, 0)
    newText = re.sub("[\r\n]*<(tr|TR)>[\r\n]*", "\r\n|-----\r\n", newText, 0)
    
    ##################
    # normal <td> without arguments
    newText = re.sub("[\r\n]+<(td|TD)>([\w\W]*?)<\/(TD|td)>",
                     "\r\n| \\2\r\n", newText, 0)         

    ##################
    # normal <td> with arguments
    newText = re.sub("[\r\n]+<(td|TD)([^>]*?)>([\w\W]*?)<\/(TD|td)>",
                     "\r\n|\\2 | \\3", newText, 0)

    # WARNING: this sub might eat cells of bad HTML, but most likely it
    # will correct errors
    newText, n = re.subn("[\r\n]+<(td|TD)>([^\r\n]*?)<(td|TD)>",
                         "\r\n| \\2\r\n", newText, 0)
    warnings = warnings + n
    
    # fail save, sometimes it's a <td><td></tr>
    #        newText, n = re.subn("[\r\n]+<(td|TD)>([^<]*?)<(td|TD)><\/(tr|TR)>",
    #                             "\r\n| \\2\r\n", newText, 0)
    #        newText, n = re.subn("[\r\n]+<(td|TD)([^>]*?)>([^<]*?)<(td|TD)><\/(tr|TR)>",
    #                             "\r\n|\\2| \\3\r\n", newText, 0)
    #
    newText, n = re.subn("[\r\n]+<(td|TD)([^>]+?)>([^\r\n]*?)<\/(td|TD)>",
                         "\r\n|\\2 | \\3\r\n", newText, 0)
    warnings = warnings + n
    
    # fail save. sometimes people forget </td>
    # <td> without arguments, with missing </td> 
    newText, n = re.subn("<(td|TD)>([^<]*?)[\r\n]+",
                         "\r\n| \\2\r\n", newText, 0)
    warnings = warnings + n

    # <td> with arguments, with missing </td> 
    newText, n = re.subn("[\r\n]*<(td|TD)([^>]*?)>([\w\W]*?)[\r\n]+",
                         "\r\n|\\2 | \\3\r\n", newText, 0)
    if n > 0:
        print 'Found <td> without </td>. This shouldn\'t cause problems.'

    newText, n = re.subn("<(td|TD)>([\w\W]*?)[\r\n]+",
                         "\r\n| \\2\r\n", newText, 0)
    warnings = warnings + n


    ##################
    # Garbage collecting ;-)
    newText = re.sub("<td>[\r\n]*<\/tr>", "", newText, 0)
    newText = re.sub("[\r\n]*<\/[Tt][rRdDhH]>", "", newText, 0)
    
    ##################
    # OK, that's only theory but works most times.
    # Most browsers assume that <th> gets a new row and we do the same
    #        newText, n = re.subn("([\r\n]+\|\ [^\r\n]*?)([\r\n]+\!)",
    #                             "\\1\r\n|-----\\2", newText, 0)
    #        warnings = warnings + n
    # adds a |---- below for the case the new <tr> is missing
    #        newText, n = re.subn("([\r\n]+\!\ [^\r\n]*?[\r\n]+)(\|\ )",
    #                             "\\1|-----\r\n\\2", newText, 0)
    #        warnings = warnings + n
    
    
    ##################
    # most <th> come with '''title'''. Senseless in my eyes cuz
    # <th> should be bold anyways.
    newText = re.sub("[\r\n]+\!([^'\n\r]*)([']{3})?([^'\r\n]*)([']{3})?",
                     "\r\n!\\1\\3", newText, 0)
    
    ##################
    # kills indention within tables. Be warned, it might seldom bring
    # bad results.
    # True by default. Set 'deIndentTables = False' in user-config.py
    if config.deIndentTables:
        num = 1
        while num != 0:
            newText, num = re.subn("(\{\|[\w\W]*?)\n[ \t]+([\w\W]*?\|\})",
                                   "\\1\r\n\\2", newText, 0)
            
    ##################
    # kills additional spaces after | or ! or {|
    # This line was creating problems, so I commented it out --Daniel
    # newText = re.sub("[\r\n]+\|[\t ]+?[\r\n]+", "\r\n| ", newText, 0)
    # kills trailing spaces and tabs
    newText = re.sub("\r\n(.*)[\t\ ]+[\r\n]+", "\r\n\\1\r\n", newText, 0)
    # kill extra new-lines
    newText = re.sub("[\r\n]{4,}(\!|\|)", "\r\n\\1", newText, 0);


    ##################        
    # shortening if <table> had no arguments/parameters
    newText = re.sub("[\r\n]+\{\|[\ ]+\| ", "\r\n\{| ", newText, 0)
    # shortening if <td> had no articles
    newText = re.sub("[\r\n]+\|[\ ]+\| ", "\r\n| ", newText, 0)
    # shortening if <th> had no articles
    newText = re.sub("\n\|\+[\ ]+\|", "\n|+ ", newText, 0)
    # shortening of <caption> had no articles
    newText = re.sub("[\r\n]+\![\ ]+\| ", "\r\n! ", newText, 0)
    
    ##################
    # proper attributes
    num = 1
    while num != 0:
        newText, num = re.subn(r'([\r\n]+(\!|\||\{\|)[^\r\n\|]+)[ ]+\=[ ]+([\w]+)(\s)',
                               '\\1="\\3"\\4', newText, 0)
    # again proper attributes
    num = 1
    while num != 0:
        newText, num = re.subn('([\r\n]+(\{\||\!|\|)([^\r\n\|]+))\=' +
                               '([\w]+?)([\W]{1})',
                               '\\1="\\4"\\5', newText, 0)

    ##################
    # merge two short <td>s
    num = 1
    while num != 0:
        newText, num = re.subn("[\r\n]+(\|[^\|\-\}]{1}[^\n\r]{0,35})" +
                               "[\r\n]+(\|[^\|\-\}]{1}[^\r\n]{0,35})[\r\n]+",
                               "\r\n\\1 |\\2\r\n", newText, 0)
    ####
    # add a new line if first is * or #
    newText = re.sub("[\r\n]+\| ([*#]{1})", "\r\n|\r\n\\1", newText,0)
    
    ##################
    # strip <center> from <th>
    newText = re.sub("([\r\n]+\![^\r\n]+?)<center>([\w\W]+?)<\/center>",
                     "\\1 \\2", newText, 0)
    # strip align="center" from <th> because the .css does it
    # if there are no other attributes than align, we don't need that | either
    newText = re.sub("([\r\n]+\! +)align\=\"center\" +\|",
                     "\\1", newText, 0)
    # if there are other attributes, simply strip the align="center"
    newText = re.sub("([\r\n]+\![^\r\n\|]+?)align\=\"center\"([^\n\r\|]+?\|)",
                     "\\1 \\2", newText, 0)
    
    ##################
    # kill additional spaces within arguments
    num = 1
    while num != 0:
        newText, num = re.subn("[\r\n]+(\||\!)([^|\r\n]*?)[ \t]{2,}([^\r\n]+?)",
                               "\r\n\\1\\2 \\3", newText, 0)
        
    ##################
    # I hate those long lines because they make a wall of letters
    # Off by default, set 'splitLongParagraphs = True' in user-config.py
    if config.splitLongParagraphs:
        num = 1
        while num != 0:
            newText, num = re.subn("(\r\n[A-Z]{1}[^\n\r]{200,}?[a-z����]\.)\ ([A-Z���]{1}[^\n\r]{200,})",
                                   "\\1\r\n\\2", newText, 0)
            
    ##################
    if newText!=text:
        import difflib
        if config.DEBUG:
            print text
            print newText
        elif not quietMode:
            for line in difflib.ndiff(text.split('\n'), newText.split('\n')):
                if line[0] == '-':
                    wikipedia.output(line)
            for line in difflib.ndiff(text.split('\n'), newText.split('\n')):
                if line[0] == '+':
                    wikipedia.output(line)

        if config.table2wikiAskOnlyWarnings and warnings == 0:
            doUpload="y"
        else:
            if config.table2wikiSkipWarnings:
                doUpload="n"
            else:
                print "There were " + str(warnings) + " replacement(s) that"
                print " might result bad output"
                doUpload=raw_input('Is it correct? [y|N]')
                    

        if doUpload == 'y':
            warn = ""
            if warnings > 0:
                warn = " - " + str(warnings) + " warnings!"
            status, reason, data = pl.put(newText, myComment[wikipedia.chooselang(wikipedia.mylang,myComment)] + warn)
            print status,reason
            fixedSites = fixedSites + " " + article
        else:
            notFixedSites = notFixedSites + " " + article
            print "OK. I'm not uploading"
    else:
        print "No changes were necessary in " + article
        notFixedSites = notFixedSites + " " + article
    print "\n"
        
print "\tFollowing pages were corrected\n" + fixedSites
print "\n\tFollowing pages had errors and were not corrected\n" + notFixedSites
                  


