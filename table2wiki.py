#!/usr/bin/python
# -*- coding: iso8859-1  -*-
"""
Nifty script to convert HTML-tables to Wikipedia's syntax.

SELECT CONCAT('"', cur_title, '"')
       FROM cur
       WHERE cur_text LIKE '%<table%'
       ORDER BY cur_title


FEATURES
Save against missing </td>
Corrects attributes of tags

KNOW BUGS
Broken HTML-tables will most likely result in broken wiki-tables!
Please check every article you change.

WARNINGS
Indented HTML-tables will result in ugly wiki-tables.
You can kill indentions but it's switched off by default.

"""

# (C) 2003 Thomas R. Koll, <tomk32@tomk32.de>
#
# Distribute under the terms of the PSF license.
__version__='$Id$'

import re,sys,wikipedia

mylang = 'de'
myComment = 'User-controlled Bot: table syntax updated'
fixedSites = ''
notFixedSites = ''

deIndentTables = 0
splitLongSentences = 0

DEBUG=0

for arg in sys.argv[1:]:
    if wikipedia.argHandler(arg):
        pass
    else:
        if DEBUG:
            f = open("table2wiki.testTable")
            text = f.read()
        else:
            pl = wikipedia.PageLink(mylang, arg)
            try:
                text = pl.get()
            except wikipedia.NoPage:
                print "ERROR: couldn't find " + arg
                continue
        
        newText = text

        # every open-tag gets a new line.
        newText = re.sub("(\<[Tt]{1}[dDHhRr]{1}([^>]*)\>)",
                         "\n\\1", newText, 0)
        # bring every tag into one single line.
        num = 1
        while num != 0:
            newText, num = re.subn("(\<[^>\n\r]+?)[\r\n]+(\>)",
                                   "\\1 \\2", newText, 0)

        # the <table> tag
        newText = re.sub("<(TABLE|table) ([\w\W]*?)>([\w\W]*?)<(tr|TR)>",
                         "{| \\2\n\\3", newText, 0)
        newText = re.sub("<(TABLE|table)>([\w\W]*?)<(tr|TR)>",
                         "{|\n\\2", newText, 0)
        newText = re.sub("\<(TABLE|table) ([\w\W]*?)\>[\n ]*",
                         "{| \\2\n", newText, 0)
        newText = re.sub("\<(TABLE|table)\>[\n ]*",
                         "{|\n", newText, 0)
        # end </table>
        newText = re.sub("[\s]*<\/(TABLE|table)\>", "\n|}", newText, 0)


        # captions
        newText = re.sub("<caption ([\w\W]*?)>([\w\W]*?)<\/caption>",
                         "\n|+\\1 | \\2", newText, 0)
        newText = re.sub("<caption>([\w\W]*?)<\/caption>",
                         "\n|+ \\1", newText, 0)


        #very simple <tr>
        newText = re.sub("[\r\n]+<(tr|TR)([^>]*?)\>", "\r\n|-----\\2\r\n", newText, 0)

        #<th> often people don't write them within <tr>, be warned!
        newText = re.sub("[\r\n]+<(TH|th)([^>]*?)\>([\w\W]*?)\<\/(th|TH)\>",
                         "\n!\\2 | \\3\r\n", newText, 0)
        # fail save. sometimes people forget </th>
        newText = re.sub("[\r\n]+<(th|TH)\>([\w\W]*?)\n",
                         "\n! \\2\n", newText, 0)
        newText = re.sub("[\r\n]+<(th|TH)([^>]*?)\>([\w\W]*?)\n",
                         "\n!\\2 | \\3\n", newText, 0)


        # normal <td>
        newText = re.sub("[\r\n]+\<(td|TD)\>([\w\W]*?)\<\/(TD|td)\>",
                         "\n| \\2\n", newText, 0)         
        newText = re.sub("[\r\n]+\<(td|TD)([^>]*?)\>([\w\W]*?)\<\/(TD|td)\>",
                         "\n|\\2 | \\3\n", newText, 0)
        # fail save. sometimes people forget </td>
        newText = re.sub("[\r\n]+<(td|TD)\>([\w\W]*?)\n",
                         "\n| \\2\n", newText, 0)
        newText = re.sub("[\r\n]+<(td|TD)([^>]*?)\>([\w\W]*?)\n",
                         "\n|\\2 | \\3\n", newText, 0)



        # Garbage collecting ;-)
        newText = re.sub("[\r\n]*\<\/[Tt][rRdDhH]\>", "", newText, 0)

        # OK, that's only theory but works most times.
        # Most browsers assume that <th> gets a new row and we do the same
        newText = re.sub("([\r\n]+\|\ [^\r\n]*?)([\r\n]+\!)", "\\1\r\n|-----\\2",
                         newText, 0)

        # most <th> come with '''title'''. Senseless in my eyes cuz
        # <th> should be bold anyways.
        newText = re.sub("[\r\n]+\!([^'\n\r]*)([']{3})?([^'\r\n]*)([']{3})?",
                         "\n!\\1\\3", newText, 0)

        # kills indention within tables. Be warned, it might bring
        # bad results.
        if deIndentTables:
            num = 1
            while num != 0:
                newText, num = re.subn("(\{\|[\w\W]*?)\n[ \t]+([\w\W]*?\|\})",
                                       "\\1\n\\2", newText, 0)

        # kills spaces after | or ! or {|
        newText = re.sub("[\r\n]+\|[\t ]*\n", "\r\n| ", newText, 0)
        # kills trailing spaces and tabs
        newText = re.sub("([^\|])[\t\ ]+[\r\n]+", "\\1\r\n", newText, 0)

        # kill extra new-lines
        newText = re.sub("[\r\n]+(\!|\|)", "\r\n\\1", newText, 0);
        # shortening if <table> had no arguments/parameters
        newText = re.sub("[\r\n]+\{\|[\ ]+\| ", "\r\n\[| ", newText, 0)
        # shortening if <td> had no args
        newText = re.sub("[\r\n]+\|[\ ]+\| ", "\r\n| ", newText, 0)
        # shortening if <th> had no args
        newText = re.sub("\n\|\+[\ ]+\|", "\n|+ ", newText, 0)
        # shortening of <caption> had no args
        newText = re.sub("[\r\n]+\![\ ]+\| ", "\r\n! ", newText, 0)

        # merge two short <td>s (works only once :-(
        num = 1
        while num != 0:
            newText, num = re.subn("[\r\n]+(\|[^\|\-\}]{1}[^\n\r]{0,35})" +
                                   "[\r\n]+\|[^\|\-\}]{1}([^\r\n]{0,35})[\r\n]+",
                                   "\r\n\\1 || \\2\r\n", newText, 0)


        # proper attributes
        num = 1
        while num != 0:
            newText, num = re.subn(r'([\r\n]+(\!|\||\{\|)[^\r\n\|]+)[ ]+\=[ ]+([^\s>]+)(\s)',
                                   '\\1="\\3"\\4', newText, 0)
        # again proper attributes
        num = 1
        while num != 0:
            newText, num = re.subn('([\r\n]+(\{\||\!|\|)([^\r\n\|]+))\=' +
                                   '([^\"\s]+?)([\W]{1})',
                                   '\\1="\\4"\\5', newText, 0)

        if splitLongSentences:
            num = 1
            while num != 0:
                newText, num = re.subn("(\r\n[^\n\r]{2x00,}?[a-zäöüß]\.)\ ([A-ZÄÖÜ]{1}[^\n\r]{100,})",
                                       "\\1\r\n\\2", newText, 0)
                
        if newText!=text:
            import difflib
            if DEBUG:
                print text
                print newText
            else:
                for line in difflib.ndiff(text.split('\n'),
                                          newText.split('\n')):
                    if line[0] in ['+','-']:
                        print unicode(repr(line)[2:-1])
                    
            #print "\nOriginal text\n" + text
            #print "\nModified text\n" + newText

            doUpload=raw_input('Is it correct? [y|N]')


            if doUpload == 'y':
                status, reason, data = pl.put(newText, myComment)
                print status,reason
                fixedSites = fixedSites + " " + arg
            else:
                notFixedSites = notFixedSites + " " + arg
                print "OK. I'm not uploading"
        else:
            print "No changes were necessary in " + arg
            notFixedSites = notFixedSites + " " + arg
            
print "\tFollowing pages were corrected\n" + fixedSites
print "\n\tFollowing pages had errors and were not corrected\n" + notFixedSites
                  
