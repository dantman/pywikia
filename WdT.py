# -*- coding: utf-8  -*-
"""
(C) 2003 Thomas R. Koll, <tomk32@tomk32.de>
 Distribute under the terms of the PSF license.
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
    print "getting: " + file,
    parser.parse(host + file)
    data = ch.result
    print " parsing..."
    # now we parse the file


    # and make a result text for wikipedia
    skip = []
    for a in data:
        if localArticleList != "":
            import string
            for line in fileinput.input(localArticleList):
                try:
                    if unicode(string.strip(line)) == a:
                        skip.append(a)
                        print "skipping: " + a
                        break
                except:
                    pass
            fileinput.close()
    for a in skip:
        del data[a]
    print data

    if data:
        newText = newText + "\n* '''" +  XMLfiles[file] + ":''' \n"
    for a in data:
        if DEBUG:
            print "checking: " + a
        newText = newText + "[[" + a + "]] ([" + \
                  data[a]['link'] + ' ' + data[a]['count'] + ']) \n'
    if DEBUG:
        print newText

pl = wikipedia.PageLink(wikipedia.mylang, article)
text = pl.get()
newText = text + newText


if DEBUG:
    print newText
else:
    status, reason, data = pl.put(newText, "WdT: updated")
    print status, reason
