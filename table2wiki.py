#!/usr/bin/python
# -*- coding: iso-8859-1  -*-
"""
Nifty script to convert HTML-tables to Wikipedia's syntax.


-file:filename
    will read any [[wikipedia link]] and use these articles

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

WARNING!
Indented HTML-tables will result in ugly wiki-tables.
You can kill indentions but it's switched off by default.

"""

# (C) 2003 Thomas R. Koll, <tomk32@tomk32.de>
#
# Distribute under the terms of the PSF license.
__version__='$Id$'

import re,sys,wikipedia,config,time

myComment = 'User-controlled Bot: table syntax updated'
fixedSites = ''
notFixedSites = ''
notFoundSites = ''
quietMode = False # use -quiet to get less output

articles = []    
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
    else:
        articles.append(arg)
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
            newText, num = re.subn("(\<[^!]{1}[^>\n\r]*?)[\r\n]+",
                                   "\\1 ", newText, 0)
            warnings = warnings + num

        ##################
        # every open-tag gets a new line.
        newText = re.sub("(\<[tT]{1}[dDhHrR]{1}([\w\W]*?)\>)",
                         "\r\n\\1", newText, 0)



        ##################
        # the <table> tag
        newText = re.sub("[\r\n]*?\<(?i)(TABLE|table) ([\w\W]*?)>([\w\W]*?)<(tr|TR)>",
                         "\r\n{| \\2\n\\3", newText, 0)
        newText = re.sub("[\r\n]*?\<(TABLE|table)>([\w\W]*?)<(tr|TR)>",
                         "\r\n{|\n\\2", newText, 0)
        newText = re.sub("[\r\n]*?\<(TABLE|table) ([\w\W]*?)\>[\n ]*",
                         "\r\n{| \\2\n", newText, 0)
        newText = re.sub("[\r\n]*?\<(TABLE|table)\>[\n ]*",
                         "\r\n{|\n", newText, 0)
        # end </table>
        newText = re.sub("[\s]*<\/(TABLE|table)\>", "\r\n|}", newText, 0)


        ##################
        # captions
        newText = re.sub("<caption ([\w\W]*?)>([\w\W]*?)<\/caption>",
                         "\n|+\\1 | \\2", newText, 0)
        newText = re.sub("<caption>([\w\W]*?)<\/caption>",
                         "\n|+ \\1", newText, 0)

        ##################
        # very simple <tr>
        newText = re.sub("[\r\n]+<(tr|TR)([^>]*?)\>", "\r\n|-----\\2\r\n", newText, 0)


        ##################
        # <th> often people don't write them within <tr>, be warned!
        newText = re.sub("[\r\n]+<(TH|th)([^>]*?)\>([\w\W]*?)\<\/(th|TH)\>",
                         "\n!\\2 | \\3\r\n", newText, 0)
        # fail save. sometimes people forget </th>
        newText, n = re.subn("[\r\n]+<(th|TH)\>([\w\W]*?)\n",
                             "\n! \\2\n", newText, 0)
        warnings = warnings + n
        newText, n = re.subn("[\r\n]+<(th|TH)([^>]*?)\>([\w\W]*?)\n",
                             "\n!\\2 | \\3\n", newText, 0)
        warnings = warnings + n


        ##################
        # normal <td>
        newText = re.sub("[\r\n]+\<(td|TD)\>([\w\W]*?)\<\/(TD|td)\>",
                         "\n| \\2\n", newText, 0)         
        newText = re.sub("[\r\n]+\<(td|TD)([^>]*?)\>([\w\W]*?)\<\/(TD|td)\>",
                         "\n|\\2 | \\3\n", newText, 0)
        # WARNING: this sub might eat cells of bad HTML, but most likely it
        # will correct errors
        newText, n = re.subn("[\r\n]+\<(td|TD)\>([^\r\n]*?)\<(td|TD)\>",
                             "\n| \\2\n", newText, 0)
        warnings = warnings + n
        newText, n = re.subn("[\r\n]+\<(td|TD)([^>]+?)\>([^\r\n]*?)\<(td|TD)\>",
                             "\n|\\2 | \\3\n", newText, 0)
        warnings = warnings + n
        # fail save. sometimes people forget </td>
        newText, n = re.subn("[\r\n]+<(td|TD)\>([\w\W]*?)\n",
                         "\n| \\2\n", newText, 0)
        warnings = warnings + n
        newText, n = re.subn("[\r\n]+<(td|TD)([^>]*?)\>([\w\W]*?)\n",
                         "\n|\\2 | \\3\n", newText, 0)
        warnings = warnings + n


        ##################
        # Garbage collecting ;-)
        newText = re.sub("\<td\>[\r\n]*\<\/tr\>", "", newText, 0)
        newText = re.sub("[\r\n]*\<\/[Tt][rRdDhH]\>", "", newText, 0)

        ##################
        # OK, that's only theory but works most times.
        # Most browsers assume that <th> gets a new row and we do the same
        newText, n = re.subn("([\r\n]+\|\ [^\r\n]*?)([\r\n]+\!)",
                             "\\1\r\n|-----\\2", newText, 0)
        warnings = warnings + n
        # adds a |---- below for the case the new <tr> is missing
        newText, n = re.subn("([\r\n]+\!\ [^\r\n]*?[\r\n]+)(\|\ )",
                             "\\1|-----\r\n\\2", newText, 0)
        warnings = warnings + n


        ##################
        # most <th> come with '''title'''. Senseless in my eyes cuz
        # <th> should be bold anyways.
        newText = re.sub("[\r\n]+\!([^'\n\r]*)([']{3})?([^'\r\n]*)([']{3})?",
                         "\n!\\1\\3", newText, 0)

        ##################
        # kills indention within tables. Be warned, it might seldom bring
        # bad results.
        # True by default. Set 'deIndentTables = False' in user-config.py
        if config.deIndentTables:
            num = 1
            while num != 0:
                newText, num = re.subn("(\{\|[\w\W]*?)\n[ \t]+([\w\W]*?\|\})",
                                       "\\1\n\\2", newText, 0)

        ##################
        # kills additional spaces after | or ! or {|
        newText = re.sub("[\r\n]+\|[\t ]+?\n", "\r\n| ", newText, 0)
        # kills trailing spaces and tabs
        newText = re.sub("([^\|])[\t\ ]+([\r\n]+)", "\\1\\2", newText, 0)
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
        # merge two short <td>s
        num = 1
        while num != 0:
            newText, num = re.subn("[\r\n]+(\|[^\|\-\}]{1}[^\n\r]{0,35})" +
                                   "[\r\n]+(\|[^\|\-\}]{1}[^\r\n]{0,35})[\r\n]+",
                                   "\r\n\\1 |\\2\r\n", newText, 0)

        ##################
        # proper attributes
        num = 1
        while num != 0:
            newText, num = re.subn(r'([\r\n]+(\!|\||\{\|)[^\r\n\|]+)[ ]+\=[ ]+([a-zA-Z0-9%]+)(\s)',
                                   '\\1="\\3"\\4', newText, 0)
        # again proper attributes
        num = 1
        while num != 0:
            newText, num = re.subn('([\r\n]+(\{\||\!|\|)([^\r\n\|]+))\=' +
                                   '([a-zA-Z0-9%]+?)([\W]{1})',
                                   '\\1="\\4"\\5', newText, 0)

        ##################
        # strip <center> from <th>
        newText = re.sub("(\n\![^\r\n]+?)\<center\>([\w\W]+?)\<\/center\>",
                         "\\1 \\2", newText, 0)
        # strip align="center" from <th> because the .css does it
        newText = re.sub("(\n\![^\r\n\|]+?)align\=\"center\"([^\n\r\|]+?\|)",
                         "\\1 \\2", newText, 0)

        ##################
        # kill additional spaces within arguments
        num = 1
        while num != 0:
            newText, num = re.subn("\n(\||\!)([^|\r\n]*?)[ \t]{2,}([^\r\n]+?)",
                                   "\n\\1\\2 \\3", newText, 0)

        ##################
        # I hate those long line because they make a wall of letters
        # Off by default, set 'splitLongParagraphs = True' in user-config.py
        if config.splitLongParagraphs:
            num = 1
            while num != 0:
                newText, num = re.subn("(\r\n[^\n\r]{200,}?[a-zäöüß]\.)\ ([A-ZÄÖÜ]{1}[^\n\r]{200,})",
                                       "\\1\r\n\\2", newText, 0)

        ##################
        if newText!=text:
            import difflib
            if config.DEBUG:
                print text
                print newText
            elif not quietMode:
                for line in difflib.ndiff(text.split('\n'),
                                          newText.split('\n')):
                    if line[0] in ['+','-']:
                        print unicode(repr(line)[2:-1])

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
                status, reason, data = pl.put(newText, myComment + warn)
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
                  


