#!/usr/bin/python
# -*- coding: utf-8  -*-
# A tool to see the recentchanges ordered by user instead of by date. This
# is meant to be run as a CGI script.
# Currently only works on Dutch Wikipedia, I do intend to make it more generally
# usable.
# Permission has been asked to run this on the toolserver.
__version__ = '$Id$'

import cgi
import cgitb
import re
cgitb.enable()

form = cgi.FieldStorage()
print "Content-Type: text/html"
print
print
print "<html>"
print "<head>"
print '<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />'
print '<style type="text/css" media="screen,projection">/*<![CDATA[*/ @import "http://nl.wikipedia.org/skins-1.5/monobook/main.css?59"; /*]]>*/</style>'
print "</head>"
print "<body>"
print "<!--"
import wikipedia
print "-->"
mysite = wikipedia.getSite()
special = mysite.family.special_namespace(mysite.lang)

post = 'title=%s:Recentchanges' % special
for element in form:
    post += '&%s=%s'%(element,form[element].value)
if not 'limit' in form:
    post += '&limit=1000'

text = mysite.getUrl('/w/index.php?%s'%post)
text = text.split('\n')
rcoptions = False
lines = []
Ruser = re.compile('title=\"%s\:Contributions\/([^\"]*)\"' % special)
Rnumber = re.compile('tabindex=\"(\d*)\"')
count = 0
for line in text:
    if rcoptions:
        if line.find('gesch') > -1:
            try:
                user = Ruser.search(line).group(1)
            except AttributeError:
                user = None
            count += 1
            lines.append((user,count,line))
            print
    elif line.find('rcoptions') > -1:
        print line.replace("/w/index.php?title=%s:Recentchanges&amp;" % special,"rcsort.py?")
        rcoptions = True
lines.sort()
last = 0

for line in lines:
    if line[0] != last:
        print "</ul>"
        if line[0] == None:
            print "<h2>Gebruiker onbekend</h2>"
        else:
            wikipedia.output(u"<h2>%s</h2>"%line[0], toStdout=True)
        print "<ul>"
        last = line[0]
    wikipedia.output(line[2].replace('href="/w','href="http://nl.wikipedia.org/w'), toStdout = True)
    print

print "</ul>"
print "<p>&nbsp;</p>"
print "</body>"
print "</html>"
