# -*- coding: utf-8 -*-
"""
Script to resolve double redirects, and to delete broken redirects.
Requires access to MediaWiki's maintenance pages or to a SQL dump file. Delete function requires
adminship.

Syntax:

    python redirect.py action [argument]

where action can be one of these:

* double - fix redirects which point to other redirects
* broken - delete redirects where targets don\'t exist. Requires adminship.

and argument can be:

* namespace:n - Namespace to process. Works only with a sql dump
* sql - retrieve information from a local dump (http://download.wikimedia.org).

if this argument isn't given, info will be loaded from the maintenance page of
the live wiki.
argument can also be given as "-sql:filename.sql".

NOTE: For resolving redirects, please use solve_disambiguation.py -redir.
"""
#
# (C) Daniel Herding, 2004
#
# Distributed under the terms of the PSF license.
#
__version__='$Id$'
#
from __future__ import generators
import wikipedia, config
import re, sys

# Summary message for fixing double redirects
msg_double={
    'en':u'Robot: Fixing double redirect',
    'de':u'Bot: Korrigiere doppelten Redirect',
    'is':u'Vélmenni: Lagfæri tvöfalda tilvísun',
    }

# Reason for deleting broken redirects
reason_broken={
    'en':u'Robot: Redirect target doesn\'t exist',
    'de':u'Bot: Weiterleitungsziel existiert nicht',
    }


def get_redirects_from_dump(sqlfilename):
    '''
    Loads a local sql dump file, looks at all pages which have the redirect flag
    set, and finds out where they're pointing at.
    Returns a dictionary where the redirect names are the keys and the redirect
    targets are the values.
    NOTE: if the redirect isn't in the main namespace, the returned key will be
    prefixed by the default namespace identifiers. See full_title() in dump.py.
    '''
    dict = {}
    # open sql dump and read page titles out of it
    dump = sqldump.SQLdump(sqlfilename, wikipedia.myencoding())
    redirR = wikipedia.redirectRe(wikipedia.getSite())
    for entry in dump.entries():
        if (entry.id % 10000) == 0:
            print 'Checking entry %s' % (entry.id)
        if namespace != -1 and namespace != entry.namespace:
            continue
        if entry.redirect:
            m = redirR.search(entry.text)
            if m == None:
                # NOTE: due to a MediaWiki bug, many articles are falsely marked with the
                # redirect flag, so this warning will eventually show up several times.
                # Ask a MediaWiki developer to fix the SQL database.
                wikipedia.output(u'WARNING: can\'t extract the target of redirect %s, ignoring' % (entry.full_title()))
            else:
                target = m.group(1)
                # There might be redirects to another wiki. Ignore these.
                for code in wikipedia.getSite().family.langs.keys():
                    if target.startswith(code + ':'):
                        # TODO: doesn't seem to work
                        wikipedia.output(u'NOTE: Ignoring %s which is a redirect to %s:' % (entry.full_title(), code))
                        target = None
                        break
                # if the redirect does not link to another wiki
                if target:
                    target = target.replace(' ', '_')
                    # remove leading and trailing whitespace
                    target = target.strip()
                    # capitalize the first letter
                    if not wikipedia.getSite().nocapitalize:
                        target = target[0].upper() + target[1:]
                    if target.find('#') != -1:
                        target = target[:target.index('#')]
                    if target.find('|') != -1:
                        wikipedia.output(u'HINT: %s is a redirect with a pipelink.' % entry.full_title())  
                        target = target[:target.index('|')]
                    dict[entry.full_title()] = target
    return dict
    
def retrieve_broken_redirects(source):
    if source == None:
        mysite = wikipedia.getSite()
        # retrieve information from the live wiki's maintenance page
        host = mysite.hostname()
        # broken redirect maintenance page's URL
        url = mysite.maintenance_address('brokenredirects', default_limit = False)
        print 'Retrieving maintenance page...' 
        maintenance_txt, charset = wikipedia.getUrl(host,url)
        
        # regular expression which finds redirects which point to a non-existing page inside the HTML
        Rredir = re.compile('\<li\>\<a href=\"\/w\/wiki.phtml\?title=(.*?)&amp;redirect=no\"')
    
        redir_names = Rredir.findall(maintenance_txt)
        print 'Retrieved %d redirects from maintenance page.\n' % len(redir_names)
        for redir_name in redir_names:
            yield redir_name
    else:
        print 'Step 1: Getting a list of all redirects'
        redirs = get_redirects_from_dump(sqlfilename)
        print 'Step 2: Getting a list of all page titles'
        dump = sqldump.SQLdump(sqlfilename, wikipedia.myencoding())
        # We save page titles in a dictionary where all values are None, so we
        # use it as a list. "dict.has_key(x)" is much faster than "x in list"
        # because "dict.has_key(x)" uses a hashtable while "x in list" compares
        # x with each list element
        pagetitles = {}
        for entry in dump.entries():
            pagetitles[entry.full_title()] = None
        print 'Step 3: Comparing.'
        brokenredirs = []
        for (key, value) in redirs.iteritems():
            if not pagetitles.has_key(value):
                yield key

def delete_broken_redirects(source):
    # get reason for deletion text
    reason = wikipedia.translate(wikipedia.getSite(), reason_broken)

    for redir_name in retrieve_broken_redirects(source):
        redir_page = wikipedia.PageLink(wikipedia.getSite(), redir_name)
        try:
            target_name = redir_page.getRedirectTo(read_only = True)
        except wikipedia.IsNotRedirectPage:
            wikipedia.output(u'%s is not a redirect.' % redir_page.linkname())
        except wikipedia.NoPage:
            wikipedia.output(u'%s doesn\'t exist.' % redir_page.linkname())
        except wikipedia.LockedPage:
            wikipedia.output(u'%s is locked.' % redir_page.linkname())
        else:
            try:
                target_page = wikipedia.PageLink(wikipedia.getSite(), target_name)
                target_page.get(read_only = True)
            except wikipedia.NoPage:
                redir_page.delete(reason, prompt = False)
            except wikipedia.IsRedirectPage:
                wikipedia.output(u'Redirect target is also a redirect! Won\'t delete anything.')
            else:
                wikipedia.output(u'Redirect target does exist! Won\'t delete anything.')
            # idle for 1 minute
        print ''
        wikipedia.put_throttle()
        
def retrieve_double_redirects(source):
    if source == None:
        mysite = wikipedia.getSite()
        # retrieve information from the live wiki's maintenance page
        host = mysite.hostname()
        # double redirect maintenance page's URL
        url = mysite.maintenance_address('doubleredirects', default_limit = False)
        
        print 'Retrieving maintenance page...' 
        maintenance_txt, charset = wikipedia.getUrl(host,url)
    
        # regular expression which finds redirects which point to another redirect inside the HTML
        Rredir = re.compile('\<li\>\<a href=\"\/w\/wiki.phtml\?title=(.*?)&amp;redirect=no\"')
        redir_names = Rredir.findall(maintenance_txt)
        print 'Retrieved %d redirects from maintenance page.\n' % len(redir_names)
        for redir_name in redir_names:
            yield redir_name
    else:
        dict = get_redirects_from_dump(sqlfilename)
        for (key, value) in dict.iteritems():
            # check if the value - that is, the redirect target - is a
            # redirect as well
            if dict.has_key(value):
                yield key
                
def fix_double_redirects(source):
    mysite = wikipedia.getSite()
    for redir_name in retrieve_double_redirects(source):
        print ''
        redir = wikipedia.PageLink(mysite, redir_name)
        try:
            target = redir.getRedirectTo()
        except wikipedia.IsNotRedirectPage:
            wikipedia.output(u'%s is not a redirect.' % redir.linkname())
        except wikipedia.NoPage:
            wikipedia.output(u'%s doesn\'t exist.' % redir.linkname())
        except wikipedia.LockedPage:
            wikipedia.output(u'%s is locked, skipping.' % redir.linkname())
        else:
            try:
                second_redir = wikipedia.PageLink(mysite, target)
                second_target = second_redir.getRedirectTo(read_only = True)
            except wikipedia.IsNotRedirectPage:
                wikipedia.output(u'%s is not a redirect.' % second_redir.linkname())
            except wikipedia.NoPage:
                wikipedia.output(u'%s doesn\'t exist.' % second_redir.linkname())
            else:
                txt = "#REDIRECT [[%s]]" % second_target
                status, reason, data = redir.put(txt)
                print status, reason

# read command line parameters
# what the bot should do (either resolve double redirs, or delete broken redirs)
action = None
# where the bot should get his infos from (either None to load the maintenance
# special page from the live wiki, the filename of a local sql dump file)
source = None
# Which namespace should be processed when using a SQL dump
# default to -1 which means all namespaces will be processed
namespace = -1
for arg in sys.argv[1:]:
    arg = wikipedia.argHandler(arg)
    if arg:
        if arg == 'double':
            action = 'double'
        elif arg == 'broken':
            action = 'broken'
        elif arg.startswith('-sql'):
            if len(arg) == 4:
                sqlfilename = wikipedia.input(u'Please enter the SQL dump\'s filename: ')
            else:
                sqlfilename = arg[5:]
            import sqldump
            source = sqlfilename
        elif arg.startswith('-namespace:'):
            namespace = int(arg[11:])
        else:
            print 'Unknown argument: %s' % arg

if action == 'double':
    # get summary text
    wikipedia.setAction(wikipedia.translate(wikipedia.getSite(), msg_double))
    fix_double_redirects(source)
elif action == 'broken':
    delete_broken_redirects(source)
else:
    wikipedia.output(__doc__, 'utf-8')

