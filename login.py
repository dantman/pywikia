"""
Script to log the robot in to a wikipedia account.

Suggestion is to make a special account to use for robot use only. Make
sure this robot account is well known on your home wikipedia before using.
"""
#
# (C) Rob W.W. Hooft, 2003
#
# Distribute under the terms of the PSF license.
#
__version__='$Id$'

import re
import httplib
import wikipedia

# This needs to be translated for each wikipedia we want to use it on.
loginaddr={'nl':'/w/wiki.phtml?title=Speciaal:Userlogin&amp;action=submit',
           }

if 0:
    print wikipedia.getPage(wikipedia.mylang, 'Speciaal:Userlogin',do_edit=0)
    import sys
    sys.exit(0)

print "Logging in to ",wikipedia.langs[wikipedia.mylang]
username=raw_input('username: ')
password=raw_input('password: ')

# I hope this doesn't need translation
data = wikipedia.urlencode((
            ('wpName', username),
            ('wpPassword', password),
            ('wpLoginattempt', "Aanmelden & Inschrijven"),
            ('wpRemember', '1'),
            ))

headers = {"Content-type": "application/x-www-form-urlencoded"}
conn = httplib.HTTPConnection(wikipedia.langs[wikipedia.mylang])
conn.request("POST", loginaddr[wikipedia.mylang], data, headers)
response = conn.getresponse()
data = response.read()
conn.close()
#print response.status, response.reason
#print data
#print dir(response)
f=open('login.data','w')
n=0
msg=response.msg
Reat=re.compile(': (.*?);')
print repr(msg.getallmatchingheaders('set-cookie'))
for eat in msg.getallmatchingheaders('set-cookie'):
    m=Reat.search(eat)
    if m:
        n=n+1
        f.write(m.group(1)+'\n')
f.close()
if n==4:
    print "Should be logged in now"
else:
    print "Hm. Did something go wrong?"
