# -*- coding: utf-8 -*-
"""
Script to resolve double redirects, and to delete broken redirects.
Requires access to MediaWiki's maintenance pages. Delete function requires
adminship.

For syntax information, see bottom of this file.

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

# Summary message for fixing double redirects
msg_double={
    'en':'Robot: Fixing double redirect',
    'de':'Bot: Korrigiere doppelten Redirect',
    }

# Reason for deleting broken redirects
reason_broken={
    'en':'Robot: Redirect target doesn\'t exist',
    'de':'Bot: Weiterleitungsziel existiert nicht',
    }

def delete_broken_redirects():
    # get reason for deletion text
    reason = reason_broken[wikipedia.chooselang(wikipedia.mylang, reason_broken)]

    host = wikipedia.family.hostname(wikipedia.mylang)
    # broken redirect maintenance page's URL
    url = wikipedia.family.maintenance_address(wikipedia.mylang, 'brokenredirects', default_limit = False)
    print 'Retrieving maintenance page...' 
    maintenance_txt, charset = wikipedia.getUrl(host,url)
    
    # regular expression which finds redirects which point to a non-existing page inside the HTML
    Rredir = re.compile('\<li\>\<a href=\"\/w\/wiki.phtml\?title=(.*?)&amp;redirect=no\"')

    redir_names = Rredir.findall(maintenance_txt)
    print 'Retrieved %d redirects from maintenance page.\n' % len(redir_names)
    for redir_name in redir_names:
        redir_page = wikipedia.PageLink(wikipedia.mylang, redir_name)
        try:
            target_page = redir_page.getRedirectTo()
        except (wikipedia.IsNotRedirectPage, wikipedia.NoPage):
            wikipedia.output('%s doesn\'t exist or is not a redirect.')
        else:
            try:
                target_name = str(redir_page.getRedirectTo())
                target_page = wikipedia.PageLink(wikipedia.mylang, target_name)
                target_page.get()
            except wikipedia.NoPage:
                #wikipedia.output('Deleting %s...' % redir_page.linkname())
                wikipedia.deletePage(redir_page, reason, prompt = False)
            except wikipedia.IsRedirectPage():
                wikipedia.output('Redirect target is also a redirect! Won\'t delete anything.')
            else:
                wikipedia.output('Redirect target does exist! Won\'t delete anything.')
            # idle for 1 minute
        print
        wikipedia.put_throttle()
        
def fix_double_redirects():
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
        except (wikipedia.IsNotRedirectPage, wikipedia.NoPage):
            print 'The specified page is not a double redirect.\n'
            continue
        txt = "#REDIRECT [[%s]]" % second_target
        redir.put(txt)

# read command line parameters
action = ''
for arg in sys.argv[1:]:
    if wikipedia.argHandler(arg):
        pass
    elif arg == 'double':
        action = 'double'
    elif arg == 'broken':
        action = 'broken'
    else:
        print 'Unknown argument: %s' % arg

if action == 'double':
    # get summary text
    wikipedia.setAction(msg_double[wikipedia.chooselang(wikipedia.mylang, msg_double)])
    fix_double_redirects()
elif action == 'broken':
    delete_broken_redirects()
else:
    print 'Syntax: python redirect.py action'
    print 'where action can be one of these:'
    print ' * double - fix redirects which point to other redirects'
    print ' * broken - delete redirects where targets don\'t exist. Requires adminship.'
    print ''
    print 'NOTE: For resolving redirects, please use solve_disambiguation.py -redir.'
    # TODO: make this runnable from within this bot.

       
