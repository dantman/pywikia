# -*- coding: utf-8 -*-
"""
Script to resolve double redirects, and to delete broken redirects.
Requires access to MediaWiki's maintenance pages or to a SQL dump file. Delete function requires
adminship.

For syntax information, run the bot without arguments.

"""
#
# (C) Daniel Herding, 2004
#
# Distributed under the terms of the PSF license.
#
__version__='$Id$'
#
import wikipedia, config
import re, sys

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


# Loads a local sql dump file, looks at all pages which have the redirect flag
# set, and finds out where they're pointing at.
# Returns a dictionary where the redirect names are the keys and the redirect
# targets are the values.
# NOTE: if the redirect isn't in the main namespace, the returned key will be
# prefixed by the default namespace identifiers. See full_title() in dump.py.
def get_redirects_from_dump(sqlfilename):
    dict = {}
    # open sql dump and read page titles out of it
    dump = sqldump.SQLdump(sqlfilename, wikipedia.myencoding())
    # case-insensitive regular expression which takes a redirect's text
    # (that is: '#REDIRECT [[bla]]') and extracts its target (that is: bla).
    redirR = re.compile('#REDIRECT[^\[]*\[\[([^\]]+)\]\]', re.IGNORECASE)
    for entry in dump.entries():
        if entry.redirect == '1':
            m = redirR.search(entry.text)
            if m == None:
                # NOTE: due to a MediaWiki bug, many articles are falsely marked with the
                # redirect flag, so this warning will eventually show up several times.
                # Ask a MediaWiki developer to fix the SQL database.
                print 'WARNING: can\'t extract the target of redirect %s, ignoring' % (entry.full_title())
            else:
                target = m.group(1)
                target = target.replace(' ', '_')
                dict[entry.full_title()] = target
    return dict
    
def retrieve_broken_redirects(source):
    if source == None:
        # retrieve information from the live wiki's maintenance page
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
            yield redir_name
    else:
        print 'NOTE: This function is not working yet. Press Enter to continue.'
        raw_input()
        print 'Step 1: Getting a list of all redirects'
        redirs = get_redirects_from_dump(sqlfilename)
        print 'Step 2: Getting a list of all page titles'
        dump = sqldump.SQLdump(sqlfilename, wikipedia.myencoding())
        pagetitles = []
        for entry in dump.entries():
            print entry.full_title()
            pagetitles.append(entry.full_title())
        print 'Step 3: Comparing. This might take a while (or two).'
        brokenredirs = []
        for (key, value) in redirs.popitem():
            print key
            if not value in pagetitles:
                brokenredirs.append(key)
        print brokenredirs

def delete_broken_redirects(source):
    # get reason for deletion text
    reason = reason_broken[wikipedia.chooselang(wikipedia.mylang, reason_broken)]

    for redir_name in retrieve_broken_redirects(source):
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
        print ''
        wikipedia.put_throttle()
        
def retrieve_double_redirects(source):
    if source == None:
        # retrieve information from the live wiki's maintenance page
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
            yield redir_name
    else:
        dict = get_redirects_from_dump(sqlfilename)
        for (key, value) in dict.iteritems():
            # check if the value - that is, the redirect target - is a
            # redirect as well
            if dict.has_key(value):
                yield key
                
def fix_double_redirects(source):
    for redir_name in retrieve_double_redirects(source):
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
        print ''

# read command line parameters
# what the bot should do (either resolve double redirs, or delete broken redirs)
action = None
# where the bot should get his infos from (either None to load the maintenance
# special page from the live wiki, the filename of a local sql dump file)
dump = None
for arg in sys.argv[1:]:
    arg = unicode(arg, config.console_encoding)
    if wikipedia.argHandler(arg):
        pass
    elif arg == 'double':
        action = 'double'
    elif arg == 'broken':
        action = 'broken'
    elif arg.startswith('-sql'):
        if len(arg) == 4:
            sqlfilename = wikipedia.input('Please enter the SQL dump\'s filename: ')
        else:
            sqlfilename = arg[5:]
        import sqldump
        source = sqlfilename
    else:
        print 'Unknown argument: %s' % arg

if action == 'double':
    # get summary text
    wikipedia.setAction(msg_double[wikipedia.chooselang(wikipedia.mylang, msg_double)])
    fix_double_redirects(source)
elif action == 'broken':
    delete_broken_redirects(source)
else:
    print 'Syntax: python redirect.py action [argument]'
    print 'where action can be one of these:'
    print ' * double - fix redirects which point to other redirects'
    print ' * broken - delete redirects where targets don\'t exist. Requires adminship.'
    print 'and argument can be:'
    print ' * sql - retrieve information from a local dump (http://download.wikimedia.org).'
    print '         if this argument isn\'t given, info will be loaded from the maintenance'
    print '         page of the live wiki.'
    print '         argument can also be given as "-sql:filename.sql".'
    print 'NOTE: For resolving redirects, please use solve_disambiguation.py -redir.' # TODO: make this runnable from within this bot.
