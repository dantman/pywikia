"""
Script to log the robot in to a wikipedia account.

Suggestion is to make a special account to use for robot use only. Make
sure this robot account is well known on your home wikipedia before using.

This script has no command line arguments. Please run it as such. It will ask
for your username and password (it will show your password on the screen!), log
in to your home wikipedia using this combination, and store the resulting
cookies (containing your password in encoded form, so keep it secured!) in a
file named login.data

The wikipedia library will be looking for this file and will use the login
information if it is present.

To log out, throw away the login.data file that is created.

You can only log in to one wikipedia at a time,
and it should be the one mentioned in username.dat.
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

if not wikipedia.special.has_key(wikipedia.mylang):
    print "Please add the translation for the Special: namespace in"
    print "Your home wikipedia to the wikipedia.py module"
    import sys
    sys.exit(1)
    
# This needs to be translated for each wikipedia we want to use it on.
loginaddr='/w/wiki.phtml?title=%s:Userlogin&amp;action=submit'

print "Logging in to ",wikipedia.langs[wikipedia.mylang]
username=raw_input('username: ')
password=raw_input('password: ')

if wikipedia.mylang=='en':
    pl=wikipedia.PageLink('en','Wikipedia:Bots')
    text=pl.get()
    if not '[[User:%s'%username in text:
        print "Your username is not listed on [[Wikipedia:Bots]]"
        print "Please make sure you are allowed to use the robot"
        print "Before actually using it!"
        
# I hope this doesn't need translation
data = wikipedia.urlencode((
            ('wpName', username),
            ('wpPassword', password),
            ('wpLoginattempt', "Aanmelden & Inschrijven"),
            ('wpRemember', '1'),
            ))

headers = {"Content-type": "application/x-www-form-urlencoded"}
conn = httplib.HTTPConnection(wikipedia.langs[wikipedia.mylang])
pagename = loginaddr%wikipedia.special[wikipedia.mylang]
conn.request("POST", pagename, data, headers)
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
    print "Hm. Did something go wrong? Wrong password?"
