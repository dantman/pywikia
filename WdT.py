# -*- coding: utf-8  -*-
"""
(C) 2004 Thomas R. Koll, <tomk32@tomk32.de>
 Distribute under the terms of the PSF license.

This bot consists of WdT.py and WdTXMLpaser.py and
imports XML-files into Wikipedia.
The XML-file contains the an automatic generated list
of the most significant word in current events
which the bot use as article-links and compare to
a local list of all articles. Only the not-yet-written
articles will be saved on wikipedia.

"""

__version__='$Id$'


import WdTXMLParser,httplib,wikipedia,re,datetime,xml.sax,fileinput

DEBUG = 1
host = "http://wortschatz.uni-leipzig.de/wort-des-tages/RDF/WdT/"

localArticleList = "Stichwortliste_de_Wikipedia_2004-04-17_sortiert.txt"

XMLfiles = {
    "ort.xml"           : "Orte",
    "ereignis.xml"      : "Eregnisse",
    "kuenstler.xml"     : "Kunst, Kultur und Wissenschaft", 
    "organisation.xml"  : "Organisationen",
    "politiker.xml"     : "Politker",
    "schlagwort.xml"    : u"Schlagwörter",
    "sportler.xml"      : "Sportler",
    "sport.xml"         : "Sport",
    "person.xml"        : "sonstige"
    }
article = "Wikipedia:Wort_des_Tages"

newText = "\n== " + str(datetime.date.today()) + " =="

#start the xml parser
ch = WdTXMLParser.WdTXMLParser()
parser = xml.sax.make_parser()
parser.setContentHandler(ch)

# first we get the XML-File
for file in XMLfiles:
    print "\ngetting: " + file,
    parser.parse(host + file)
    data = ch.result
    print " parsing..."
    # now we parse the file


    # and make a result text for wikipedia
    skip = []
    if localArticleList != "":
        import string
        for a in data:
            print "\nchecking: " + a,
            for line in fileinput.input(localArticleList):
                if unicode(string.strip(line),"iso-8859-1") == a:
                    skip.append(a)
                    print "..,skipping ",
                    break
            fileinput.close()
    for a in skip:
        del data[a]
    if DEBUG >= 2:
        print data

    if data:
        newText = newText + "\n* '''" +  XMLfiles[file] + ":''' \n"
    for a in data:
        newText = newText + "[[" + a + "]] ([" + \
                  data[a]['link'] + ' ' + data[a]['count'] + ']) \n'
    if DEBUG >= 2:
        print newText

pl = wikipedia.PageLink(wikipedia.mylang, article)
text = pl.get()
newText = text + newText


if DEBUG:
    print newText
else:
    status, reason, data = pl.put(newText, "WdT: updated")
    print status, reason
