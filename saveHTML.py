# -*- coding: utf-8  -*-
"""
(C) 2004 Thomas R. Koll, <tomk32@tomk32.de>
 Distribute under the terms of the PSF license.

This bot downloads the HTML-pages of articles and
saves the interesting parts, i.e. the article-text
and the footer to a file like Hauptseite.txt.


Options:

      -o:    Specifies the output-directory where to save the files   
"""

import wikipedia,httplib,StringIO,re,sys

def extractArticle(data):
    """ takes a string with the complete HTML-file
    and returns the article which is contained in
    <div id='article'> and  the pagestats which
    contain information on last change """
    
    s = StringIO.StringIO(data)
    rPagestats = re.compile('.*(\<span id\=\'pagestats\'\>.*\<\/span\>).*')
    rBody = re.compile('.*<div id\=\"bodyContent\">.*')
    rFooter = re.compile('.*<div id\=\"footer\">.*')
    rDivOpen = re.compile('.*<div ')
    rDivClose = re.compile('.*<\/div>.*')
    divLevel = 0
    divLast = -1
    inArticle = 0
    inFooter  = 0
    result = {'article':"",
              'footer':""}
    for line in s:
        if rDivOpen.match(line):
            divLevel = divLevel + 1
        if rBody.match(line):
            inArticle = 1
            divLast = divLevel-1
        elif rFooter.match(line):
            divLast = divLevel-1
            inFooter  = 1
        if inArticle:
            result['article'] += line
        elif inFooter:
            result['footer'] += line
        if rDivClose.match(line):
            divLevel = divLevel - 1
            if divLevel == divLast:
                inArticle = 0
                inFooter = 0
                divLast = -1
    return result

lang = wikipedia.mylang
sa = []
output_directory = ""
for arg in sys.argv[1:]:
    if arg.startswith("-lang:"):
        lang = arg[6:]
    if arg.startswith("-file:"):
        for pl in wikipedia.PageLinksFromFile(arg[6:]):
            sa.append(pl)
    if arg.startswith("-o:"):
        output_directory = arg[3:]
    else:
        sa.append(arg)

headers = {"Content-type": "application/x-www-form-urlencoded", 
           "User-agent": "RobHooftWikiRobot/1.0"}
conn = httplib.HTTPConnection(wikipedia.family.hostname(wikipedia.mylang))

for article in sa:
    article = unicode(article, "utf-8")
    conn.request("GET", '/wiki/'+article, "", headers)
    response = conn.getresponse()
    data = response.read()
    conn.close()
    data = extractArticle(data)
    f = open (output_directory + article + ".txt", 'w')
    f.write (data['article'] + '\n' + data['footer'])
    f.close
    print "saved " + article
