"""
This is a wikipedia robot.

Automatically make redirect pages for months with capital letters

This is a specialized one-time only robot that is tailored for the Dutch
situation. In Dutch, months are written with a small letter, but many people
make the mistake of using a capital letter. All of the pages with capital
letters were created using this script, and were added to the list of
disambiguation pages such that it raises an alert if someone refers to them.
"""
#
# (C) Rob W.W. Hooft, 2003
#
# Distribute under the terms of the PSF license.
#
__version__='$Id$'
#
import os,sys,re,wikipedia

# Summary used in the modification request
wikipedia.setAction('redirect')

debug=0
if debug:
    wikipedia.langs={'test':'test.wikipedia.org'}
    mylang='test'
else:
    mylang='nl'

def do(month):
    if debug:
        page='Robottest'

    for day in range(1,31+1):
        print day
        page="%d %s"%(day,month)
        cappage="%d_%s"%(day,month.capitalize())

        do=1
        
        # Only if the page exists
        try:        
            text=wikipedia.getPage(mylang,page)
        except wikipedia.NoPage:
            print "Page does not exist"
            do=0
        
        # Only if the redir-page does not exist
        try:        
            text=wikipedia.getPage(mylang,cappage)
        except wikipedia.NoPage:
            pass
        else:
            print "Redirect exists"
            do=0

        if do==0:
            continue

        text="#redirect [[%s]]"%page

        status,reason,data=wikipedia.putPage(mylang,cappage,text)
        print status,reason

if __name__=="__main__":
    do('september')
    do('december')

