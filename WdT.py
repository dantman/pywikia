# -*- coding: iso-8859-1  -*-
"""
(C) 2003 Thomas R. Koll, <tomk32@tomk32.de>
 Distribute under the terms of the PSF license.
"""

__version__='$Id$'


import WdTXMLParser,httplib,wikipedia,re,datetime

DEBUG = 0
host = "wortschatz.uni-leipzig.de"
baseDir = "/wort-des-tages/RDF/WdT/"
XMLfiles = {"ereignis.xml"      : "Eregnisse",
            "kuenstler.xml"     : "Kunst, Kultur und Wissenschaft", 
            "organisation.xml"  : "Organisationen",
            "ort.xml"           : "Orte",
            "politiker.xml"     : "Politker",
            "schlagwort.xml"    : "Schlagwörter",
            "sportler.xml"      : "Sportler",
            "sport.xml"         : "Sport",
            "person.xml"        : "sonstige Personen"
            }
           
article = "Wikipedia:Wort_des_Tages"

newText = str(datetime.date.today())

# first we get the XML-File
headers = {"Accept": "text/xml",
           "User-agent": "RobHooftWikiRobot/1.0"}
conn = httplib.HTTPConnection(host)
for file in XMLfiles:
    print "getting: " + file,
    conn.request("GET", baseDir + file, "", headers)
    response = conn.getresponse()
    XMLdata = unicode(response.read(), "iso-8859-1")
    # bad hack, I know
    XMLdata = re.sub("<\?.*?\?>[\r\n]*", "", XMLdata)
    print " parsing..."
    # now we parse the file
    p = WdTXMLParser.WdTXMLParser()
    try:
        p.feed(XMLdata)
        p.close()
    except:
        print p

    # and make a result text for wikipedia
    newText = newText + "\r\n* '''" +  XMLfiles[file] + ":''' "
    for a in p.results:
        newText = newText + "[[" + a + "]] ([" + \
                  p.results[a]['link'] + ' ' + p.results[a]['count'] + ']) \r\n'
    if DEBUG:
        print newText
conn.close()

pl = wikipedia.PageLink(wikipedia.mylang, article)
text = pl.get()
newText = text + unicode(newText, "iso-8859-1")
print newText

status, reason, data = pl.put(newText, "WdT: updated")
print status, reason
