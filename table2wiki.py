#!/usr/bin/python
# -*- coding: iso8859-1  -*-
"""
Nifty script to convert HTML-tables to Wikipedia's syntax.

SELECT CONCAT('"', cur_title, '"')
       FROM cur
       WHERE cur_text LIKE '%<table%'
       ORDER BY cur_title


KNOW BUGS
Broken HTML-tables will most likely result in broken wiki-tables!
Please check every article you change.

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

DEBUG=0

for arg in sys.argv[1:]:
    if wikipedia.argHandler(arg):
        pass
    else:
        pl = wikipedia.PageLink(mylang, arg)
        try:
            a="sa"
            text = pl.get()
        except wikipedia.NoPage:
            print "ERROR: couldn't find " + arg
            continue
        
        newText = text
        newText = re.sub("(\<[Tt]{1}[dDHhRr]{1}([^>]*)\>)",
                         "\n\\1", newText, 0)
        newText = re.sub("\n[ ]*\<", "\n<", newText, 0)

        #the <table> tag
        newText = re.sub("<(TABLE|table) (.*?)>([\w\W]*?)<(tr|TR)>",
                         "{| \\2\n\\3", newText, 0)
        newText = re.sub("<(TABLE|table)>([\w\W]*?)<(tr|TR)>",
                         "{|\n\\2", newText, 0)
        newText = re.sub("\<(TABLE|table) (.*?)\>[\n ]*",
                         "{| \\2\n", newText, 0)
        newText = re.sub("\<(TABLE|table)\>[\n ]*",
                         "{|\n", newText, 0)
        #end </table>
        newText = re.sub("[\s]*<\/(TABLE|table)\>", "\n|}", newText, 0)


        #captions
        newText = re.sub("<caption(.*?)>(.*?)<\/caption>",
                         "\n|+\\1 | \\2", newText, 0)
        newText = re.sub("\n\|\+[\ ]+\|", "\n|+ ", newText, 0)

        #very simple <tr>
        newText = re.sub("\n\<(tr|TR)([^>]*?)\>", "\n|-----\\2\r\n", newText, 0)

        #<th> often people don't write them within <tr>, be warned!
        newText = re.sub("[\s]*<(TH|th)([^>]*?)\>([\w\W]*?)\<\/(th|TH)\>",
                         "\n! \\2 | \\3\r\n", newText, 0)

        # sorry for the mess, but there are too many variants
        newText = re.sub("\n\<(td|TD)([^>]*)\>([\w\W]*?)\<\/(TD|td)\>",
                         "\n|\\2 | \\3\n", newText, 0)
        # fail save. sometimes people forget </td>
        newText = re.sub("<(td|TD)([^<]*)\>([\w\W]*?)\n",
                         "\n|\\2 | \\3\n", newText, 0)

        # Garbage collecting ;-)
        newText = re.sub("[\r\n]*\<\/[Tt][rRdDhH]\>", "", newText, 0)

        # OK, that's only theory but works most times.
        # Most browsers assume that <th> gets a new row and we do the same
        newText = re.sub("\n\|([^-][^|]+?)[\r\n]+\!", "|\\1\r\n|-----\r\n!",
                         newText, 0)

        # kills spaces after | or ! or {|
        newText = re.sub("[\r\n]+\|[\s]*\n", "\r\n| ", newText, 0)
        # kills trailing spaces and tabs
        newText = re.sub("[\t\ ][\t\ ]+([\r\n]){1}", "\\1", newText, 0)

        
        # kill extra new-lines
        newText = re.sub("[\r\n]+(\!|\|)", "\r\n\\1", newText, 0);
        # shortening if <table> had no arguments/parameters
        newText = re.sub("[\r\n]+\{\|[\ ]+\| ", "\r\n\[| ", newText, 0)
        # shortening if <td> had no args
        newText = re.sub("[\r\n]+\|[\ ]+\| ", "\r\n| ", newText, 0)
        # shortening if <th> had no args
        newText = re.sub("[\r\n]+\![\ ]+\| ", "\r\n! ", newText, 0)
        # merge two short <td>s (works only once :-(
        newText = re.sub("[\r\n]+(\| [^\n\r]{1,35})[\r\n]+\| ([^\r\n]{1,35})[\r\n]+",
                         "\r\n\\1 || \\2\r\n", newText, 0)
        # ain't working, yet
#        newText = re.sub('(\{\|[\w\W]*?\=)([^"][^ >]*)(.*?\|\})',
#                         '\\1"\\2"\\3', newText, 0)

                
        if newText!=text:
            import difflib
            for line in difflib.ndiff(text.split('\n'),newText.split('\n')):
                if line[0] in ['+','-']:
                    print unicode(repr(line)[2:-1])
                    
            #print "\nOriginal text\n" + text
            #print "\nModified text\n" + newText

            doUpload=raw_input('Is it correct? [y|N]')


            if doUpload == 'y' and not DEBUG:
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
                  
