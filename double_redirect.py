# -*- coding: utf-8 -*-
"""
Script to resolve double redirects. Requires access to MediaWiki's maintenance
pages.

Command line options:

None

"""
#
# (C) Daniel Herding, 2004
#
# Distributed under the terms of the PSF license.
#
__version__='$Id$'
#
import wikipedia
import re, sys, string

# Summary message
msg={
    'en':'Robot: Fixing double redirect',
    'de':'Bot: Korrigiere doppelten Redirect',
    }

def fixDoubleRedirects():
    host = wikipedia.family.hostname(wikipedia.mylang)
    # double redirect maintenance page's URL
    url = wikipedia.family.maintenance_address(wikipedia.mylang, 'doubleredirects', default_limit = False)
    
    print 'Retrieving maintenance page...' 
    maintenance_txt, charset = wikipedia.getUrl(host,url)
    
    # regular expression which finds redirects which point to another redirect inside the HTML
    Rredir = re.compile('\<li\>\<a href=\"\/w\/wiki.phtml\?title=(.*?)&amp;redirect=no\"')
    redir_names = Rredir.findall(maintenance_txt)
    print 'Retrieved %d redirects from maintenance page.\n' % len(redir_names)
    for redir_name in redir_names:
        redir = wikipedia.PageLink(wikipedia.mylang, redir_name)
        try:
            target = str(redir.getRedirectTo())
            second_redir = wikipedia.PageLink(wikipedia.mylang, target)
            second_target = str(second_redir.getRedirectTo())
        except wikipedia.IsNotRedirectPage, wikipedia.NoPage:
            print 'The specified page is not a double redirect.\n'
            continue
        txt = "#REDIRECT [[%s]]" % second_target
        redir.put(txt)

# read command line parameters
for arg in sys.argv[1:]:
    if wikipedia.argHandler(arg):
        pass
    else:
        print 'Unknown argument: %s' % arg

# get summary text
wikipedia.setAction(msg[wikipedia.chooselang(wikipedia.mylang,msg)])
fixDoubleRedirects()
